(function() {
    function init() {
        const codeBlocks = document.querySelectorAll("pre > code");
        for (let i = 0; i < codeBlocks.length; i++) {
            const block = codeBlocks[i];
            addClipboardButton(block);
        }

        document.addEventListener("click", function(evt) {
            const node = evt.target;
            if (!node.classList.contains("code-clipboard-button") || node.tagName.toUpperCase() !== "BUTTON") {
                return;
            }

            const codeBlock = node.parentNode;
            const codeText = codeBlock.textContent.slice(0, -13).trim();
            copyToClipboard(codeText);
        });
    }

    function addClipboardButton(block) {
        const html = "<i class='material-icons'>content_copy</i>";
        const btn = document.createElement("button");
        btn.className = "code-clipboard-button";
        btn.innerHTML = html;
        block.style.position = "relative";
        block.appendChild(btn);
    }


    function copyToClipboard(text) {
        var input = document.createElement('input');
        input.setAttribute('value', text);
        document.body.appendChild(input);
        input.select();
        var result = document.execCommand('copy');
        input.remove();
        return result;
     }

    window.initCodeBlockClipboardButtons = init;
})();

