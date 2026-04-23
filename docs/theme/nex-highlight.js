(function () {
  function registerNex(hljs) {
    const KEYWORDS = {
      keyword: "fn return if else while for array void",
      literal: "true false",
    };
    const STRING = {
      className: "string",
      begin: '"',
      end: '"',
      illegal: "\n",
      contains: [hljs.BACKSLASH_ESCAPE],
    };

    return {
      name: "NEX",
      aliases: ["nex"],
      keywords: KEYWORDS,
      contains: [
        hljs.COMMENT("#", "$"),
        {
          className: "type",
          begin: /\b(int|str|bool)\b/,
        },
        {
          className: "meta",
          begin: /\bany\b/,
        },
        {
          className: "built_in",
          begin: /\b(print|print_inline|version|input|intstr|strint|resize|length|reset)(?=\s*\()/,
        },
        {
          className: "title",
          begin: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/,
        },
        STRING,
        {
          className: "number",
          begin: /\b\d+\b/,
        },
        {
          className: "operator",
          begin: /==|!=|<=|>=|[+\-*/%^<>=!]/,
        },
        {
          className: "punctuation",
          begin: /[()[\]{};,]/,
        },
      ],
    };
  }

  function highlightNexBlocks() {
    if (!window.hljs) {
      return;
    }

    if (!window.hljs.getLanguage || !window.hljs.getLanguage("nex")) {
      window.hljs.registerLanguage("nex", registerNex);
    }

    document.querySelectorAll("code.language-nex").forEach((block) => {
      block.textContent = block.textContent;
      window.hljs.highlightBlock(block);
      block.classList.add("hljs");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", highlightNexBlocks);
  } else {
    highlightNexBlocks();
  }
})();
