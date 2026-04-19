(function () {
  function registerNex(hljs) {
    const KEYWORDS = {
      keyword: "if else while for",
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
          className: "built_in",
          begin: /\bprint(?=\s*\()/,
        },
        STRING,
        {
          className: "number",
          begin: /\b\d+\b/,
        },
        {
          className: "operator",
          begin: /==|!=|<=|>=|[+\-*/%<>=!]/,
        },
        {
          className: "punctuation",
          begin: /[(){};,]/,
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

    document.querySelectorAll("pre code.language-nex").forEach((block) => {
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
