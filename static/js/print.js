
function print(firstname,lastname) {
    const data = {
        firstname: firstname,
        lastname: lastname
    };

    fetch('/print/frame', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then((response) => {
      if (response.status == 200){
        return response.text();
      }
      alert('Fehlgeschlagen');
      return null;
    }).then((data) => {
        console.log(data);
        if (data == 'success') {
            alert('Wird gedruckt!');
        }
    })
}