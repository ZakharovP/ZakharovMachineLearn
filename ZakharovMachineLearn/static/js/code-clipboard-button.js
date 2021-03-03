/*
    Файл содержит код для добавления кнопки копирования кода из тэга сode в буфер,
    и добавления такой кнопки в тэг.
*/

(function() {
    /*
        Самовызывающаяся функция, в которой происходит создание и инициализация нужного кода.
        Обертывание в самовызывающуюся функцию код - чтобы изолировать область видимости и
        переменные оттуда не попали в глобальное пространство имен.
    */
    function init() {
        /*
            Основная функция добавления кнопок копирования в буфер.
            Вызывается из главной программы.
        */

        // получаем все DOM элементы тэга сode, вложенного в pre как прямой потомок
        const codeBlocks = document.querySelectorAll("pre > code");

        // в цикле проходим по всем найденным DOM элементам
        for (let i = 0; i < codeBlocks.length; i++) {
            // сам элемент
            const block = codeBlocks[i];
            // вызываем функцию добавления кнопки копирования в элемент
            addClipboardButton(block);
        }

        // добавление обработчика события клика на документ, в котором определяем то,
        // по чему был клик и если это кнопка нужно типа, копируем код из элемента - источника события
        // в буфер
        document.addEventListener("click", function(evt) {
            const node = evt.target;  // элемент, по которому был клик

            // если это не нужная кнопка, выходим
            if (!node.classList.contains("code-clipboard-button") || node.tagName.toUpperCase() !== "BUTTON") {
                return;
            }

            // получаем узел с кодом
            const codeBlock = node.parentNode;

            // получаем код (убираем мусор в конце)
            const codeText = codeBlock.textContent.slice(0, -13).trim();

            // вызываем функцию копирования в буфер
            copyToClipboard(codeText);
        });
    }

    function addClipboardButton(block) {
        /*
            Функция добавления кнопки копирования в буфер для выбранного узла
        */
        const html = "<i class='material-icons'>content_copy</i>";
        const btn = document.createElement("button");
        btn.className = "code-clipboard-button";
        btn.innerHTML = html;
        block.style.position = "relative";
        block.appendChild(btn);
    }


    function copyToClipboard(text) {
        /*
            Функция копирования в буфер.
            Так как копировать можно только выделенный текст, то нужно создать невидимый элемент input,
            в скопировать перенести текст, там его выделить и после этого поместить в буфер. В конце этот
            невидимый элемент удалить.
        */

        // создаем невидимый input
        var input = document.createElement('input');
        input.style.opacity = 0;
        input.style.pointerEvents = "none";

        // вставляем туда нужный текст
        input.setAttribute('value', text);

        // добавляем его в body
        document.body.appendChild(input);

        // выделяем его текст
        input.select();

        // вызываем команду копирования
        var result = document.execCommand('copy');

        // удаляем этот элемент
        input.remove();

        return result;
     }

    /*
        Присваиваем функцию init свойству initCodeBlockClipboardButtons глобального объекта window.
        Это нужно, чтобы данная функция была доступна извне.
    */
    window.initCodeBlockClipboardButtons = init;
})();

