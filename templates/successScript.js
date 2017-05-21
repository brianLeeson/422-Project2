// javascript imported by success.html
//


/* format of retrieved JSON Data:
    { 0: {Foster Name : "John Smith",
        Foster Email : "jsmith@email.com",
        Animal Name(s) : "Fluffy Bunny",
        Medication(s) : "Love, Hugs",
        Notes : "blah blah blah blah"}, 1: {....}, 2: {....} }
*/

var remindersJSON = null;

// AJAX request to '/generate' - get reminder calendar data
$(document).ready(function() {
    $.ajax({
        url: "/fakedata",
        type: 'GET',
        cache: false,
        success: function(reminders) {
            remindersJSON = reminders;
            console.log("success", reminders);
            var count = Object.keys(reminders).length;
            console.log("count =", count);
            var fields = ["Foster Name", "Foster Email", "Animal Name(s)", "Medication(s)", "Notes"];
            var tableRef = $("#tabletime");
            for (i = 0; i < count; i++) {
                tableRef.append('<tr' + ' id=row' + i + '>' + '</tr>');
                var rowRef = $("#row" + i );
                rowRef.append('<input type="checkbox" name="emailselect">');
                for (j = 0; j < fields.length; j++) {
                    rowRef.append('<td>' + reminders["" + i + ""][fields[j]] + '</td>' );
                }
            }
        }
    })
});

console.log(remindersJSON);

// processes form information to send selected data for emailing
function processForm() {


        $.ajax({
            type:"POST",
            url: "/send_emails",
            data: dataString,
            cache: false,
            success: function(result){
                alert(result);
            }
        });


    return False;}