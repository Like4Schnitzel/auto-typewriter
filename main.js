// run this in the browser console

const startBox = document.querySelectorAll(".ui-dialog")[1];
let charsPerTenMins;
do {
    charsPerTenMins = parseInt(prompt("How many characters per 10 minutes would you like to achieve?"));
} while (charsPerTenMins === NaN);
const msToWait = 600000 / charsPerTenMins;
const currentCharacterSpan = document.querySelector("#text_todo").children[0];

//this gets called upon the vanishing of the initial ui box
const init = (mutationsList, observer) => {
    setInterval(() => {
        const keyToPress = currentCharacterSpan.innerHTML;
        document.activeElement.dispatchEvent(new KeyboardEvent("keypress", {
            altKey: false,
            ctrlKey: false,
            key: keyToPress, // on regular keys it checks for key
            keyCode: 32 // only on spaces it checks for keycode, so we can leave it on 32
        }))
    }, msToWait);
}

const initObserver = new MutationObserver(init);
const config = { childList: true, subtree: true, attributes: true, attributeFilter: ['style'] };
initObserver.observe(startBox, config);
