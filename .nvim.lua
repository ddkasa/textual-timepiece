local enable_lsp = { "ruff", "mypy" }

local cwd = vim.fn.getcwd()

table.insert(require("dap").configurations.python, {
    type = "python",
    request = "launch",
    name = "Debug File",
    program = "${file}",
})
table.insert(require("dap").configurations.python, {
    type = "python",
    request = "launch",
    justMyCode = false,
    name = "Launch Application",
    redirectOutput = false,
    program = cwd .. "/src/textual_timepiece/__main__.py",
    cwd = cwd,
    python = cwd .. "/.venv/bin/python",
    console = "externalTerminal",
})
