vim.lsp.enable({ "ruff", "pyright" })

local cwd = vim.fn.getcwd()

require("dap-python").setup("debugpy-adapter")

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
