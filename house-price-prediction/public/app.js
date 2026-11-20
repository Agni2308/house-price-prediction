// Front end for the House Price Prediction project.
// Talks to the API: GET /api/options and POST /api/predict. The server validates everything;
// the checks here only make the form friendlier.
(function () {
  "use strict";

  var page = document.body.getAttribute("data-page");
  var KEY_RESULT = "hp_result";   // last prediction, shown on the result page
  var KEY_INPUTS = "hp_inputs";   // last form values, used by "Edit inputs"

  // ---------- small helpers ----------
  function el(tag, attrs, text) {
    var node = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { node.setAttribute(k, attrs[k]); });
    if (text !== undefined && text !== null) node.textContent = text;   // textContent keeps user text safe
    return node;
  }
  function byId(id) { return document.getElementById(id); }
  function store(key, value) { try { sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage blocked */ } }
  function load(key) { try { return JSON.parse(sessionStorage.getItem(key)); } catch (e) { return null; } }
  function forget(key) { try { sessionStorage.removeItem(key); } catch (e) { /* ignore */ } }
  function fixed(n, d) { return Number(n).toFixed(d); }
  function getJSON(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }
  function row(cells, headerFirst) {
    var tr = el("tr");
    cells.forEach(function (text, i) { tr.appendChild(el(headerFirst && i === 0 ? "th" : "td", headerFirst && i === 0 ? { scope: "row" } : null, text)); });
    return tr;
  }

  // ---------- home page ----------
  function initHome() {
    getJSON("/api/options").then(function (opts) {
      var hero = byId("hero-rows"), full = byId("results-rows"), shown = false;
      opts.models.forEach(function (m) {
        if (!m.test) return;
        hero.appendChild(row([m.label, fixed(m.test.RMSE, 2), fixed(m.test.R2, 3)], true));
        full.appendChild(row([m.label, fixed(m.test.MAE, 2), fixed(m.test.RMSE, 2), fixed(m.test.R2, 4)], true));
        shown = true;
      });
      if (shown) { byId("hero-card").hidden = false; byId("results").hidden = false; }
    }).catch(function () { /* the page still works without the live numbers */ });
  }

  // ---------- prediction form ----------
  var FIELDS = ["location", "area_type", "total_sqft", "bhk", "bath", "balcony"];

  function clearErrors() {
    var summary = byId("error-summary");
    summary.hidden = true; summary.textContent = "";
    document.querySelectorAll(".has-error").forEach(function (n) { n.classList.remove("has-error"); });
    document.querySelectorAll(".field-error").forEach(function (n) { n.remove(); });
    document.querySelectorAll("[aria-invalid]").forEach(function (n) { n.removeAttribute("aria-invalid"); });
  }

  function showErrors(errors) {
    var summary = byId("error-summary"), keys = Object.keys(errors);
    summary.textContent = "";
    summary.appendChild(el("strong", null, "Fix the highlighted " + (keys.length === 1 ? "field" : "fields") + " and try again."));
    var ul = el("ul");
    keys.forEach(function (k) {
      ul.appendChild(el("li", null, errors[k]));
      var holder = document.querySelector('[data-field="' + k + '"]');
      if (holder) {
        holder.classList.add("has-error");
        var input = holder.querySelector("input:not([type=radio]), select");
        if (input) input.setAttribute("aria-invalid", "true");
        holder.appendChild(el("p", { "class": "field-error" }, errors[k]));
      }
    });
    summary.appendChild(ul);
    summary.hidden = false;
    summary.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function formValues() {
    var values = {};
    FIELDS.forEach(function (f) { values[f] = byId(f).value; });
    var chosen = document.querySelector('input[name="model"]:checked');
    values.model = chosen ? chosen.value : "";
    return values;
  }

  function fillForm(values) {
    FIELDS.forEach(function (f) { if (values[f] !== undefined) byId(f).value = values[f]; });
    if (values.model) {
      var radio = document.querySelector('input[name="model"][value="' + values.model + '"]');
      if (radio) radio.checked = true;
    }
  }

  function initPredict() {
    var form = byId("predict-form"), status = byId("load-status"), btn = byId("submit-btn");

    getJSON("/api/options").then(function (opts) {
      status.hidden = true;

      var list = byId("location-list");
      opts.locations.concat([opts.other]).forEach(function (name) { list.appendChild(el("option", { value: name })); });
      byId("location-hint").textContent = opts.locations.length + " locations are listed. Type " + opts.other + " if yours is not there.";

      var area = byId("area_type");
      opts.area_types.forEach(function (name) { area.appendChild(el("option", { value: name }, name)); });

      var L = opts.limits;
      byId("sqft-hint").setAttribute("data-base", "Between " + L.total_sqft[0].toLocaleString() + " and " + L.total_sqft[1].toLocaleString() + " sqft.");
      byId("bhk-hint").textContent = L.bhk[0] + " to " + L.bhk[1] + ".";
      byId("bath-hint").textContent = L.bath[0] + " to " + L.bath[1] + ".";
      byId("balcony-hint").textContent = L.balcony[0] + " to " + L.balcony[1] + ". Leave blank to use the typical value, 2.";

      var choice = byId("model-choice");
      opts.models.forEach(function (m) {
        var label = el("label", { "class": "model-option" });
        var radio = el("input", { type: "radio", name: "model", value: m.key });
        if (m.key === "random_forest") radio.checked = true;
        label.appendChild(radio);
        label.appendChild(el("span", { "class": "model-name" }, m.label));
        label.appendChild(el("span", { "class": "model-text" }, m.summary));
        if (m.test) label.appendChild(el("span", { "class": "model-score" }, "Test RMSE " + fixed(m.test.RMSE, 2) + " lakhs, R\u00B2 " + fixed(m.test.R2, 3)));
        choice.appendChild(label);
      });

      var params = new URLSearchParams(window.location.search);
      if (params.get("new")) { forget(KEY_INPUTS); forget(KEY_RESULT); }
      else if (params.get("edit")) { var saved = load(KEY_INPUTS); if (saved) fillForm(saved); }
      updateAreaHint();
    }).catch(function () {
      status.textContent = "The form options could not be loaded. Check that the server is running, then reload the page.";
      btn.disabled = true;
    });

    // live "sqft per bedroom" hint
    var sqft = byId("total_sqft"), bhk = byId("bhk"), hint = byId("sqft-hint");
    function updateAreaHint() {
      var a = parseFloat(sqft.value), b = parseFloat(bhk.value), base = hint.getAttribute("data-base") || "";
      if (a > 0 && b > 0) {
        var per = Math.round(a / b);
        hint.textContent = "About " + per.toLocaleString() + " sqft per bedroom." +
          (per < 300 ? " The models were trained on houses with at least 300 sqft per bedroom." : "");
      } else {
        hint.textContent = base;
      }
    }
    sqft.addEventListener("input", updateAreaHint);
    bhk.addEventListener("input", updateAreaHint);

    byId("clear-btn").addEventListener("click", function () {
      form.reset(); clearErrors(); forget(KEY_INPUTS); updateAreaHint();
      var rf = document.querySelector('input[name="model"][value="random_forest"]'); if (rf) rf.checked = true;
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      clearErrors();
      var values = formValues();
      btn.disabled = true; btn.textContent = "Predicting\u2026";
      fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(values) })
        .then(function (r) { return r.json().then(function (body) { return { status: r.status, body: body }; }); })
        .then(function (res) {
          if (res.body && res.body.ok) {
            store(KEY_INPUTS, values);
            store(KEY_RESULT, res.body);
            window.location.href = "result.html";
          } else {
            showErrors((res.body && res.body.errors) || { request: "Something went wrong. Please try again." });
          }
        })
        .catch(function () { showErrors({ request: "Could not reach the server. Check your connection and try again." }); })
        .then(function () { btn.disabled = false; btn.textContent = "Predict price"; });
    });
  }

  // ---------- result page ----------
  function initResult() {
    var result = load(KEY_RESULT);
    if (!result) {
      byId("price").textContent = "\u2014";
      byId("no-result").hidden = false;
      return;
    }
    byId("price").textContent = result.predicted_price_text;
    byId("price-sub").textContent = "That is " + fixed(result.predicted_price_lakhs, 2) + " lakhs, predicted by " + result.model + ".";

    if (result.warnings && result.warnings.length) {
      var box = byId("warnings");
      box.appendChild(el("strong", null, "Treat this estimate with extra care."));
      var ul = el("ul");
      result.warnings.forEach(function (w) { ul.appendChild(el("li", null, w)); });
      box.appendChild(ul);
      box.hidden = false;
    }
    var rows = byId("summary-rows");
    result.summary.forEach(function (item) { rows.appendChild(row([item.label, item.value], true)); });

    var side = byId("model-side");
    side.appendChild(el("h2", null, "About " + result.model));
    side.appendChild(el("p", null, result.model_info.summary));
    side.appendChild(el("p", null, result.model_info.caution));
    if (result.test_metrics) {
      var p = el("p");
      p.appendChild(el("strong", null, "Experimental test-set result: "));
      p.appendChild(document.createTextNode("RMSE " + fixed(result.test_metrics.RMSE, 2) + " lakhs, R\u00B2 " + fixed(result.test_metrics.R2, 3) +
        ", measured on 2,354 held-out houses. This describes the model in general; it is not an error bar for this price."));
      side.appendChild(p);
    }
    byId("result-body").hidden = false;
  }

  if (page === "home") initHome();
  else if (page === "predict") initPredict();
  else if (page === "result") initResult();
})();
