//dynamic search bar

let search_bar = document.querySelector(".search-bar");

function expand() {
  search_bar.style.height = "60px";
  search_bar.style.width = "400px";
}



//dynamic form inputs

const form = document.getElementById('myForm');
const radioButtons = document.querySelectorAll('input[name="mode"]');
const conditionalInput1 = document.getElementById('conditionalInput1');
const input1 = document.getElementById('location');
const conditionalInput2 = document.getElementById('conditionalInput2');
const input2 = document.getElementById('address');
const conditionalInput3 = document.getElementById('conditionalInput3');
const input3 = document.getElementById('city');
const conditionalInput4 = document.getElementById('conditionalInput4');
const input4 = document.getElementById('state');

function handleRadioChange() {
    const selectedRadio = document.querySelector('input[name="mode"]:checked');
    if (selectedRadio) {
        const radioValue = selectedRadio.value;
        if (radioValue === 'offline') {
            conditionalInput1.classList.remove('hidden');
            conditionalInput2.classList.remove('hidden');
            conditionalInput3.classList.remove('hidden');
            conditionalInput4.classList.remove('hidden');
            input1.required = true;
            input2.required = true;
            input3.required = true;
            input4.required = true;
        } else {
            conditionalInput1.classList.add('hidden');
            conditionalInput2.classList.add('hidden');
            conditionalInput3.classList.add('hidden');
            conditionalInput4.classList.add('hidden');
            input1.required = false;
            input2.required = false;
            input3.required = false;
            input4.required = false;
        }
    }
}

radioButtons.forEach(button => {
    button.addEventListener('change', handleRadioChange);
});


document.addEventListener("DOMContentLoaded", function() {
    const textContainer = document.getElementById("text");
    const text = "Plan and Experience Unforgettable Events with B&B."; // Replace with your text
    let i = 0;

    function typeWriter() {
        if (i < text.length) {
            textContainer.innerHTML += text.charAt(i);
            i++;
            setTimeout(typeWriter, 90); // Adjust typing speed
        }
    }

    typeWriter();
});
