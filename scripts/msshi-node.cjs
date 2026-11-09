#!/usr/bin/env node
const { spawnSync } = require("node:child_process");
const path = require("node:path");

const candidates = process.platform === "win32"
  ? [["py", "-3"], ["python"], ["python3"]]
  : [["python3"], ["python"]];
const probe = "import sys; sys.exit(sys.version_info < (3, 10))";
const command = candidates.find(([python, ...args]) =>
  spawnSync(python, [...args, "-c", probe], { stdio: "ignore" }).status === 0
);
if (!command) {
  console.error("msshi requires Python 3.10 or newer.");
  process.exit(1);
}

const [python, ...args] = command;
const script = path.join(__dirname, "msshi_cli.py");
const result = spawnSync(python, [...args, "-B", "-X", "utf8", script, ...process.argv.slice(2)], {
  stdio: "inherit",
});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
