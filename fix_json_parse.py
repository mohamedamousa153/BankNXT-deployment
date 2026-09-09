import re

with open("frontend/app.jsx", "r") as f:
    content = f.read()

safe_parse_fn = """
function safeJSONParse(str, fallback = []) {
    if (!str) return fallback;
    try {
        return JSON.parse(str);
    } catch(e) {
        return fallback;
    }
}
"""

if "function safeJSONParse" not in content:
    content = safe_parse_fn + content

# Replace unsafe JSON.parse with safeJSONParse for selected_dates
content = content.replace("JSON.parse(r.selected_dates)", "safeJSONParse(r.selected_dates, [])")

# Replace toFixed to be safe
content = content.replace("r.duration_hours.toFixed(2)", "(r.duration_hours || 0).toFixed(2)")

with open("frontend/app.jsx", "w") as f:
    f.write(content)
