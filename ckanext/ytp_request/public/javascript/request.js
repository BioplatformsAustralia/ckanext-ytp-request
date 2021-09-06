$(document).ready(function() {
    $('#field-validroles').on('change', function(e) {
      var selected_role = $("#field-validroles option:selected").val();
      //Modify the URLs for accept case to add new role
      var approve_url_element = $('#request_approve_url');
      var approve_url = approve_url_element.attr('href').split('?', 2);
      newapp_url = approve_url[0] + '?role=' + selected_role;
      approve_url_element.attr('href', newapp_url);
    });
    
    $('#field-organizations').on('change', function(e) {
        //Setting the default selected roleto admin (in case editor was selected and now does not exist)
    var roles = $('#role');
        roles.val("admin").trigger("change");
        ckan.sandbox().client.call('POST', 'get_available_roles', {organization_id: $("#field-organizations option:selected").text()}, function(results) {
          var roles = $('#role');
          //Remove old values
          roles.get(0).options.length = 0;
          //Populate with news
          var result = results['result'];
          $.each(result, function(key, val) {
            roles.get(0).options[roles.get(0).options.length] = new Option(val.text, val.value);
          }); 
        });
   }); 

   $('#memberRequestModal').on('show.bs.modal', function (event) {
     var button = $(event.relatedTarget) // Button that triggered the modal
     var orgname = button.data('orgname') // Extract info from data-* attributes
     var organization = button.data('organization') // Extract info from data-* attributes
     // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
     // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
     var modal = $(this)
     modal.find('.modal-orgname').text(orgname)
     modal.find('.modal-body input').val(orgname)
     modal.find('#field-organizations').val(organization)
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
