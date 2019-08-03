var options = {
	valueNames: [
		'name',
		'born',
		'address',
		{ data: ['gender']}
	],
	page: 10,
	pagination: true
};
var userList = new List('users', options);

function resetList(){
	userList.search();
	userList.filter();
	userList.update();
	$(".filter-all").prop('checked', true);
	$('.filter').prop('checked', false);
	$('.search').val('');
	//console.log('Reset Successfully!');
};

function updateList(){
  var values_gender = $("input[name=gender]:checked").val();
	var values_address = $("input[name=address]:checked").val();
	console.log(values_gender, values_address);

	userList.filter(function (item) {
		var genderFilter = false;
		var addressFilter = false;

		if(values_gender == "all")
		{
			genderFilter = true;
		} else {
			genderFilter = item.values().gender == values_gender;

		}
		if(values_address == null)
		{
			addressFilter = true;
		} else {
			addressFilter = item.values().address.indexOf(values_address) >= 0;
		}
		return addressFilter && genderFilter
	});
	userList.update();
	//console.log('Filtered: ' + values_gender);
}

$(function(){
  //updateList();
  $("input[name=gender]").change(updateList);
	$('input[name=address]').change(updateList);

	userList.on('updated', function (list) {
		if (list.matchingItems.length > 0) {
			$('.no-result').hide()
		} else {
			$('.no-result').show()
		}
	});
});
