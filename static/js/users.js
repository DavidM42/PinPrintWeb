
function deleteAll() {
    fetch('/users/purge', {
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
            alert('Alle gelöscht!');
            location.reload();
        }
    })
}