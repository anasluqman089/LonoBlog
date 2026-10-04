(() => {
  function appendInline(parent, text) {
    const pattern = /(`[^`\n]+`|\*\*[^*\n]+\*\*|__[^_\n]+__|~~[^~\n]+~~|\*[^*\n]+\*|_[^_\n]+_|!\[[^\]\n]*\]\([^) \n]+\)|\[[^\]\n]+\]\([^) \n]+\))/g;
    let lastIndex = 0;

    for (const match of text.matchAll(pattern)) {
      const index = match.index;
      if (index > lastIndex) parent.append(document.createTextNode(text.slice(lastIndex, index)));
      const token = match[0];
      let element;
      if (token.startsWith("`")) {
        element = document.createElement("code");
        element.textContent = token.slice(1, -1);
      } else if (token.startsWith("**") || token.startsWith("__")) {
        element = document.createElement("strong");
        appendInline(element, token.slice(2, -2));
      } else if (token.startsWith("~~")) {
        element = document.createElement("del");
        appendInline(element, token.slice(2, -2));
      } else if (token.startsWith("*") || token.startsWith("_")) {
        element = document.createElement("em");
        appendInline(element, token.slice(1, -1));
      } else if (token.startsWith("![")) {
        const image = token.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
        const destination = image[2];
        if (/^(https?:|\/|\.\.?\/)/i.test(destination)) {
          element = document.createElement("img");
          element.alt = image[1];
          element.src = destination;
          element.loading = "lazy";
          element.decoding = "async";
        } else {
          parent.append(document.createTextNode(token));
          lastIndex = index + token.length;
          continue;
        }
      } else {
        const link = token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
        const anchor = document.createElement("a");
        anchor.textContent = link[1];
        const destination = link[2];
        if (/^(https?:|mailto:|\/|#|\.\.?\/)/i.test(destination)) {
          anchor.href = destination;
          if (/^https?:/i.test(destination)) {
            anchor.target = "_blank";
            anchor.rel = "noopener noreferrer";
          }
        } else {
          anchor.removeAttribute("href");
          anchor.setAttribute("aria-label", `${link[1]} (unsafe link omitted)`);
        }
        element = anchor;
      }
      parent.append(element);
      lastIndex = index + token.length;
    }

    if (lastIndex < text.length) parent.append(document.createTextNode(text.slice(lastIndex)));
  }

  function renderMarkdown(container, source) {
    const lines = source.replace(/\r\n?/g, "\n").split("\n");
    const fragment = document.createDocumentFragment();
    const isTableSeparator = (line) => /^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
    let index = 0;

    while (index < lines.length) {
      const line = lines[index];
      if (!line.trim()) {
        index += 1;
        continue;
      }

      const fence = line.match(/^\s*```([a-zA-Z0-9_-]*)\s*$/);
      if (fence) {
        index += 1;
        const codeLines = [];
        while (index < lines.length && !/^\s*```\s*$/.test(lines[index])) {
          codeLines.push(lines[index]);
          index += 1;
        }
        if (index < lines.length) index += 1;
        const pre = document.createElement("pre");
        const code = document.createElement("code");
        if (fence[1]) code.className = `language-${fence[1]}`;
        code.textContent = codeLines.join("\n");
        pre.append(code);
        fragment.append(pre);
        continue;
      }

      const heading = line.match(/^(#{1,6})\s+(.+?)\s*#*$/);
      if (heading) {
        const element = document.createElement(`h${heading[1].length}`);
        appendInline(element, heading[2]);
        fragment.append(element);
        index += 1;
        continue;
      }

      if (/^\s*(---+|___+|\*\*\*+)\s*$/.test(line)) {
        fragment.append(document.createElement("hr"));
        index += 1;
        continue;
      }

      if (/^\s*>/.test(line)) {
        const quote = document.createElement("blockquote");
        while (index < lines.length && /^\s*>/.test(lines[index])) {
          const paragraph = document.createElement("p");
          appendInline(paragraph, lines[index].replace(/^\s*>\s?/, ""));
          quote.append(paragraph);
          index += 1;
        }
        fragment.append(quote);
        continue;
      }

      const tableSeparator = index + 1 < lines.length && isTableSeparator(lines[index + 1]);
      if (line.includes("|") && tableSeparator) {
        const cellsFor = (row) => row.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
        const table = document.createElement("table");
        const head = document.createElement("thead");
        const headerRow = document.createElement("tr");
        cellsFor(line).forEach((text) => {
          const cell = document.createElement("th");
          appendInline(cell, text);
          headerRow.append(cell);
        });
        head.append(headerRow);
        table.append(head);
        index += 2;
        const tableBody = document.createElement("tbody");
        while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
          const row = document.createElement("tr");
          cellsFor(lines[index]).forEach((text) => {
            const cell = document.createElement("td");
            appendInline(cell, text);
            row.append(cell);
          });
          tableBody.append(row);
          index += 1;
        }
        table.append(tableBody);
        fragment.append(table);
        continue;
      }

      const listMatch = line.match(/^\s*(?:([-*+])|(\d+)\.)\s+(.+)$/);
      if (listMatch) {
        const ordered = Boolean(listMatch[2]);
        const list = document.createElement(ordered ? "ol" : "ul");
        while (index < lines.length) {
          const itemMatch = lines[index].match(/^\s*(?:([-*+])|(\d+)\.)\s+(.+)$/);
          if (!itemMatch || Boolean(itemMatch[2]) !== ordered) break;
          const item = document.createElement("li");
          const task = !ordered && itemMatch[3].match(/^\[([ xX])\]\s+(.+)$/);
          if (task) {
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.disabled = true;
            checkbox.checked = task[1].toLowerCase() === "x";
            item.append(checkbox, document.createTextNode(" "));
            appendInline(item, task[2]);
          } else {
            appendInline(item, itemMatch[3]);
          }
          list.append(item);
          index += 1;
        }
        fragment.append(list);
        continue;
      }

      const paragraphLines = [line];
      index += 1;
      while (index < lines.length && lines[index].trim()
        && !/^\s*```/.test(lines[index])
        && !/^(#{1,6})\s+/.test(lines[index])
        && !/^\s*>/.test(lines[index])
        && !/^\s*(?:[-*+]|\d+\.)\s+/.test(lines[index])
        && !/^\s*(---+|___+|\*\*\*+)\s*$/.test(lines[index])
        && !(lines[index].includes("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1]))) {
        paragraphLines.push(lines[index]);
        index += 1;
      }
      const paragraph = document.createElement("p");
      appendInline(paragraph, paragraphLines.join("\n"));
      fragment.append(paragraph);
    }

    container.replaceChildren(fragment);
  }

  window.renderMarkdown = renderMarkdown;
  window.insertEmojiAtCursor = function insertEmojiAtCursor(field, emoji) {
    const start = field.selectionStart ?? field.value.length;
    const end = field.selectionEnd ?? start;
    field.setRangeText(emoji, start, end, "end");
    field.focus();
    field.dispatchEvent(new Event("input", { bubbles: true }));
  };
})();
