# NEX Syntax for VS Code

This folder contains a minimal VS Code extension that provides:

- file association for `.nex`
- comment handling for `#`
- bracket and auto-closing configuration
- TextMate syntax highlighting for the current NEX surface language

## Local use

1. Open VS Code.
2. Open the Extensions view.
3. Choose `...` > `Install from VSIX...` after packaging, or use `Developer: Install Extension from Location...` if available in your setup.
4. Point VS Code at this folder:

```text
editors/vscode/nex-syntax
```

## Local use from WSL

If you are using VS Code through WSL, a simple way to expose the extension to
the remote server is to symlink the folder into the WSL extension directory:

```bash
mkdir -p ~/.vscode-server/extensions && ln -s "$(pwd)" ~/.vscode-server/extensions/local.nex-syntax
```

Run that command from inside:

```text
editors/vscode/nex-syntax
```

After that, reload the VS Code window.

## Covered syntax

The grammar highlights:

- keywords such as `fn`, `return`, `if`, `else`, `while`, `for`, `array`, and `void`
- primitive types such as `int`, `str`, and `bool`
- the special builtin-only type marker `any`
- booleans, numbers, strings, comments
- builtin functions such as `print`, `input`, `intstr`, `strint`, `resize`, `length`, and `reset`
- ordinary function definitions and calls

The extension is intentionally lightweight and can be extended later with
snippets, semantic tokens, code folding improvements, or a packaged VSIX
release workflow.
