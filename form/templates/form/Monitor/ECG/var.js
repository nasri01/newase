
$( "#id_s1_e1_hr" )
    .focusout(function() {
      // alert($( "#id_s1_e1_comment" ).val());
      if($( "#id_s1_e1_hr" ).val() <=0){
        $("#id_s1_e1_hr").css("background-color", "#f24858");
      $("#id_s1_e1_hr").css("color", "white");
      }
      else if($( "#id_s1_e1_hr" ).val() ==1){
        $("#id_s1_e1_hr").css("background-color", "white");
      $("#id_s1_e1_hr").css("color", "black");
      }
      
      // $( "#id_s1_e1_comment" ).text( "focusout fired: " + focus + "x" );
      // $( "#id_s1_e1_comment" ).css('background-color','red');
    });