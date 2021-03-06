# Creating a Module

A module is just a class named "module" that has some basic methods

## Creating the server side module

The server side module needs the following properties

- `provides` (the name of the module, a string)
- `version` (also a string)
- `listeners`. A list of threads to start. Ignore this for now

And the following methods

- `format`. A method that will take the payload from the client and return the data to be put into the database
- `get_format`. This returns information for how the web interface will display graphs for your module
- `generate_request`. This returns the payload that will be send to the client for a regularly scheduled request.

`provides` and `version` are self explanatory, leave `listeners` as an empty list for now.

`generate_request` can return None or False or whatever until you decide what you want to do with the client.

`get_format` we can write later. For now, if you don't want any graphs, have it return an empty list.

`format` is what allows you to log data into the database. When the module on the client sends you a message, it goes directly into the first argument of `format`. The official return type should be a list of lists. Each sub-list has three things, an integer data category, a style string (leave this as an empty string for now) and a float y value for the point on the graph.

So if you're writing a cpu module and the client module sent you `35`, the return value should look like `[[0, "", 35]]`

If it sent you data for all four cores, it may look something like `[[0, "", 35], [1, "", 42], [2, "", 32], [3, "", 12]]`, best written as `[[x, "", payload[x]] for x in range(len(payload))]`

If we were given only the average, you may want to change `get_format` to return something like this: `[[[0], "", ["%", "CPU Percentage"]]]`. 

In this, 0 is the data category we put it into the database under, the empty string is for the graph options which can be ignored right now, `"%"` is label and "CPU Percentage" is the graph name.

If we were given all four cores and stored them in the categories 0, 1, 2 and 3, and want four seperate graphs, it would look like this: `[[[0], "", ["%", "CPU Percentage"]],[[1], "", ["%", "CPU Percentage"]],[[2], "", ["%", "CPU Percentage"]],[[3], "", ["%", "CPU Percentage"]]]`. Realistically, however, you would write it like this: `[[[x], "", ["%", "CPU Percentage"]] for x in range(4)]`

This would produce four graphs with one line on each graph. If, however, we wanted one graph with four lines on it, it would look like this: `[[[0, 1, 2, 3], "", ["%", "CPU Percentage"]]]`

### Style and Graph Options

The style string in `format` is applied to that point when it is graphed. For example you could write code saying that if the cpu percentage is above 90, set it to `"point {fill-color: red;}"`, otherwise make the fill color black. For more information see [TODO Link](the Google Charts documentation)

The graph options, like `"pointSize: 6, dataOpacity: 0.3"`, are passed directly to google charts as well.

### Events

In `__init__` you are passed two arguments, `register` and the enum `triggers`. 

`register` has two required arguments, a module (i.e. `self`) and an integer trigger. The third and optional argument specifies what method should be run when the event is fired, and defaults to `module.trigger_called`

For a catch-all you should write a method called `trigger_called` that takes two arguments, the trigger and the function `send_request`. You should have in your __init__ something like `register(self, triggers.SHUTDOWN)` and `self.triggers = triggers`

In `trigger_called` you would have something like `if trigger == self.triggers.SHUTDOWN:` followed by your code to do something when the server is stopped. You can also register for the events triggers.USER and triggers.CLIENT, or another integer for a module-specific trigger.

An alternative would be to put in `__init__` something like `register(self, triggers.SHUTDOWN, self.on_shutdown)` and write a method called `on_shutdown` with your code.

To call a module-specific trigger you need a listener. Write a method, for example called `my_listener`, and set your `listeners` property to `[my_listener]`. `my_listener` will have to take the arguments `event` and `update_metadata`. An example of `my_listener` would look like this:

    def my_listener(self, event, update_metadata):
    	while True:
    		time.sleep(10)
    		if some_condition:
    			event(1000)

To listen for this, you would need to, in `__init__` add either `register(self, 1000)` or `register(self, 1000, self.handler_for_my_custom_event)`. In either case, you may want something like this:

	send_request(self, payload)

Payload is passed directly to the client module. You could also add a third optional argument as a list of the client IDs to receive the request.

The `send_request` method is given to the handler and not the listener itself because you can register to recieve events that have no associated listeners, like startup, shutdown, or when a new client connects.

## Writing the client module

The client module is very similar. `__init__` is still passed `register` and `triggers`, listeners work the same way (though they are only passed `event`, not `update_metadata`), and if you don't pass a third argument to register it still defaults to `module.trigger_called`

The main difference is that you need a method called `server_request`. When the server sends the client a query, it also sends a payload, which is passed in as the first argument to the method. The return value of `server_request` is sent as the payload back to the server and passed into the `format` method of the server module.