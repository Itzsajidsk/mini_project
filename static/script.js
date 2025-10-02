function calculateFLAMES() {
    let name1 = document.getElementById("name1").value.toLowerCase().replace(/\s+/g, "");
    let name2 = document.getElementById("name2").value.toLowerCase().replace(/\s+/g, "");

    let nameArr1 = name1.split("");
    let nameArr2 = name2.split("");
    
    nameArr1.forEach(letter => {
        let index = nameArr2.indexOf(letter);
        if (index !== -1) {
            nameArr2.splice(index, 1);
            nameArr1.splice(nameArr1.indexOf(letter), 1);
        }
    });
    
    let remainingCount = nameArr1.length + nameArr2.length;
    let flames = ["F", "L", "A", "M", "E", "S"];
    let index = 0;
    
    while (flames.length > 1) {
        index = (index + remainingCount - 1) % flames.length;
        flames.splice(index, 1);
    }
    
    let resultMap = {
        "F": "Friends 🤝👨👩",
        "L": "Lover ❤️💛",
        "A": "Attraction 💖👀",
        "M": "Marriage 👰👨👩",
        "E": "Enemy 💀💥",
        "S": "Sister 👩👩"
    };
    
    document.getElementById("result").innerHTML = `Your Relationship: 
        <span style="background: -webkit-linear-gradient(45deg, #ff6a00, #ee0979);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;">
            ${flames[0]} - ${resultMap[flames[0]].split(" ")[0]}
        </span> 
        ${resultMap[flames[0]].split(" ").slice(1).join(" ")}`;

    // Save the entered names to the server (relationships table). It's silent to the UI.
    try {
        fetch('/save_relationship', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name1: document.getElementById('name1').value.trim(), name2: document.getElementById('name2').value.trim() })
        }).then(res => {
            // optional: log for debugging
            // console.log('save relationship status', res.status);
        }).catch(err => console.error('save relationship error', err));
    } catch (e) {
        console.error('fetch save relationship failed', e);
    }
}

// Theme Toggle
function toggleTheme() {
    document.body.classList.toggle('light-theme');
}

