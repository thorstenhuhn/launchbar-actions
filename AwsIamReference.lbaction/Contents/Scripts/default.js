var stateFile = Action.cachePath + '/state.json';

function run() {
	if (File.exists(stateFile)) {
		return File.readJSON(stateFile)
	}
	return getServices();
}

function getServices() {
	try {
		var services = HTTP.getJSON('https://raw.githubusercontent.com/widdix/complete-aws-iam-reference/master/tools/serviceNames.json', 5.0);
		// LaunchBar.log(JSON.stringify(services));
		result = [];
		if (services && services.data) {
			var keys = Object.keys(services.data);
			keys.sort();
			LaunchBar.log(JSON.stringify(keys));
			for (var i = 0; i < keys.length; i++) {
				result.push({
					title: keys[i] + ": " + services.data[keys[i]],
					icon: 'font-awesome:fa-th-list',
					url: 'https://iam.cloudonaut.io/reference/' + keys[i] + '.html'
				});
			}
			File.writeJSON(result, stateFile);
		}
		return result;
	} catch(exception) {
		LaunchBar.log('Error getServices ' + exception);
		LaunchBar.alert('Error getServices ' + exception);
	}
	return {};
}

