document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Turn off default button send behaviour
  // document.querySelector('input[type="submit"]').disabled = true;

  // Add event listener to send email button
  document.querySelector('input[type="submit"]').addEventListener('click', send_email);
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Add the email table header if it does not exist
  if(document.getElementById("email-table") == null){
    const element = document.createElement('div');
    element.innerHTML = '<table class="table" id="email-table">' +
      '<thead>' +
      '<thead>' +
      '<tr>' +
      '<th scope="col">Sender</th>' +
      '<th scope="col">Subject</th>' +
      '<th scope="col">Date</th>' +
      '</tr>' +
      '</thead>' +
      '<tbody id="emails-table-body">'+
      '</tbody>'+
      '</table>';
  document.querySelector('div[id="emails-view"]').append(element);
  }

  let tableBody = document.querySelector('tbody[id="emails-table-body"]');

  // Clear old emails
  tableBody.innerHTML = '';

  // Fetch the emails
  let fetch_url = `emails/${mailbox}`

  fetch(fetch_url)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(function (email){
      console.log(email);
      const temp_element = document.createElement('tr');
      temp_element.classList.add(`${email.read?'read':'unread'}`)
      temp_element.innerHTML= `<td>${email.sender}</td>` +
          `<td>${email.subject}</td>` +
          `<td>${email.timestamp}</td>`
      tableBody.append(temp_element);
      temp_element.addEventListener('click', ()=>display_email(email.id));
    })
});


}

function send_email(){
  // get email data
  let recipients = document.querySelector('#compose-recipients').value;
  let subject = document.querySelector('#compose-subject').value;
  let body = document.querySelector("#compose-body").value;

  fetch('/emails', {
  method: 'POST',
  body: JSON.stringify({
      recipients: `${recipients}`,
      subject: `${subject}`,
      body: `${body}`
      })
  })
  .then(response => response.json())
  .then(result => {
    // Print result
    console.log(result);
    console.log('test');
    });
}

function display_email(number){

  document.querySelector('#email-table').style.display = 'none';
  document.querySelector('#emails-view').innerHTML = `<h3>Test</h3>`;

  fetch(`/emails/${number}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email)
      fetchedEmail = email;
  });
}