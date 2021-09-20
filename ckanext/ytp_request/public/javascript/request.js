$(document).ready(function() {
    $('#field-validroles').on('change', function(e) {
      var selected_role = $("#field-validroles option:selected").val();
      //Modify the URLs for accept case to add new role
      var approve_url_element = $('#request_approve_url');
      var approve_url = approve_url_element.attr('href').split('?', 2);
      newapp_url = approve_url[0] + '?role=' + selected_role;
      approve_url_element.attr('href', newapp_url);
    });
    
   $('#memberRequestModal').on('show.bs.modal', function (event) {
     var button = $(event.relatedTarget) // Button that triggered the modal
     var orgname = button.data('orgname') // Extract info from data-* attributes
     var organization = button.data('organization') // Extract info from data-* attributes
     var action = button.data('action') // Extract info from data-* attributes
     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
     var modal = $(this)
     modal.find('.modal-orgname').text(orgname)
     modal.find('.modal-body input').val(orgname)
     modal.find('#field-organizations').val(organization)
     $('#membership-request-create-form').attr('action', action)
   });

   $('#memberRequestRejectModal').on('show.bs.modal', function (event) {
     var button = $(event.relatedTarget) // Button that triggered the modal
     var action = button.data('action') // Extract info from data-* attributes
     var username = button.data('username') // Extract info from data-* attributes
     var organization = button.data('organization') // Extract info from data-* attributes
     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
     var modal = $(this)
     modal.find('.modal-details').text(organization + ' from ' + username)
     $('#membership-request-reject-form').attr('action', action)
   });
});
