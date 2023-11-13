(function($) {
  'use strict';
  if ($("#timepicker-example").length) {
    $('#timepicker-example').datetimepicker({
      format: 'LT'
    });
  }
  if ($(".color-picker").length) {
    $('.color-picker').asColorPicker();
  }
  if ($("#datepicker-popup").length) {
    $('#datepicker-popup').datepicker({
      enableOnReadonly: true,
      todayHighlight: true,
    });
  }
  if ($("#inline-datepicker").length) {
    $('#inline-datepicker').datepicker({
      enableOnReadonly: true,
      todayHighlight: true,
    });
  }
  if ($(".datepicker-autoclose").length) {
    $('.datepicker-autoclose').datepicker({
      autoclose: true
    });
  }
  if ($('input[name="date-range"]').length) {
    $('input[name="date-range"]').daterangepicker();
  }

  if ($('.input-daterange').length) {
    // Initialize the datepicker for both date inputs
    $('#date-from, #date-to').datepicker({
      format: 'yyyy-mm-dd',
      todayHighlight: true,
      autoclose: true
    });
  
    // Get the current date
    var currentDate = new Date();
  
    // Calculate the last day of the 7-day range before the current date
    var lastDay = new Date(currentDate);
    lastDay.setDate(currentDate.getDate() - 6);
  
    // Set the initial date values for date-from and date-to
    $('#date-from').datepicker('setDate', lastDay);
    $('#date-to').datepicker('setDate', currentDate);
  
    // Set the maxDate for both date inputs to the current date
    $('#date-from, #date-to').datepicker('setEndDate', currentDate);
  }

  if ($('.date-default').length) {
    // Initialize the datepicker for the date input
    $('#date').datepicker({
      format: 'yyyy-mm-dd',
      todayHighlight: true,
      autoclose: true
    });
  
    // Get the current date
    var currentDate = new Date();
  
    // Set the initial date value for date-from
    $('#date').datepicker('setDate', currentDate);
  
    // Set the maxDate for date-from to the current date
    $('#date').datepicker('setEndDate', currentDate);
  }
  
  
})(jQuery);