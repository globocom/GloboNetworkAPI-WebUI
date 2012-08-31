/**
 * jQuery UI PickList Widget
 *
 * Copyright (c) 2012 Jonathon Freeman <jonathon@awnry.com>
 * Distributed under the terms of the MIT License.
 *
 * http://code.google.com/p/jquery-ui-picklist/
 */
(function($)
{
	$.widget("awnry.pickList",
	{
		options:
		{
			// Container classes
			mainClass:                  "pickList",
			listContainerClass:         "pickList_listContainer",
			sourceListContainerClass:   "pickList_sourceListContainer",
			controlsContainerClass:     "pickList_controlsContainer",
			targetListContainerClass:   "pickList_targetListContainer",
			listClass:                  "pickList_list",
			sourceListClass:            "pickList_sourceList",
			targetListClass:            "pickList_targetList",
			clearClass:                 "pickList_clear",

			// List item classes
			listItemClass:              "pickList_listItem",
			richListItemClass:          "pickList_richListItem",
			selectedListItemClass:      "pickList_selectedListItem",

			// Control classes
			addAllClass:                "pickList_addAll",
			addClass:                   "pickList_add",
			removeAllClass:             "pickList_removeAll",
			removeClass:                "pickList_remove",

			// Control labels
			addAllLabel:                "&#8595;",
			addLabel:                   "&#8595;",
			removeAllLabel:             "&#8593;",
			removeLabel:                "&#8593;",

			// List labels
			listLabelClass:             "pickList_listLabel",
			sourceListLabel:            "Disponível",
			sourceListLabelClass:       "pickList_sourceListLabel",
			targetListLabel:            "Selecionado",
			targetListLabelClass:       "pickList_targetListLabel",

			// Sorting
			sortItems:                  true,
			sortAttribute:              "label",

			// Name of custom value attribute for list items
			listItemValueAttribute:     "pickList:value",

			// Additional list items
			items:						[]
		},

		_create: function()
		{
			var self = this;

			self._buildPickList();
			self._refresh();
		},

		_buildPickList: function()
		{
			var self = this;

			self._trigger("beforeBuild");

			self.pickList = $("<div/>")
					.hide()
					.addClass(self.options.mainClass)
					.insertAfter(self.element)
					.append(self._buildSourceList())
					.append(self._buildControls())
					.append(self._buildTargetList())
					.append( $("<div/>").addClass(self.options.clearClass) );

			self._populateLists();

			self.element.hide();
			self.pickList.show();

			self._trigger("afterBuild");
		},

		_buildSourceList: function()
		{
			var self = this;

			var container = $("<div/>")
					.addClass(self.options.listContainerClass)
					.addClass(self.options.sourceListContainerClass)
					.css({
						"-moz-user-select": "none",
						"-webkit-user-select": "none",
						"user-select": "none",
						"-ms-user-select": "none"
					})
					.each(function()
					{
						this.onselectstart = function() { return false; };
					});

			var label = $("<div/>")
					.text(self.options.sourceListLabel)
					.addClass(self.options.listLabelClass)
					.addClass(self.options.sourceListLabelClass);

			self.sourceList = $("<ul/>")
					.addClass(self.options.listClass)
					.addClass(self.options.sourceListClass)
					.delegate("li", "click", { pickList: self }, self._changeHandler);

			container
					.append(label)
					.append(self.sourceList);

			return container;
		},

		_buildTargetList: function()
		{
			var self = this;

			var container = $("<div/>")
					.addClass(self.options.listContainerClass)
					.addClass(self.options.targetListContainerClass)
					.css({
						"-moz-user-select": "none",
						"-webkit-user-select": "none",
						"user-select": "none",
						"-ms-user-select": "none"
					})
					.each(function()
					{
						this.onselectstart = function() { return false; };
					});

			var label = $("<div/>")
					.text(self.options.targetListLabel)
					.addClass(self.options.listLabelClass)
					.addClass(self.options.targetListLabelClass);

			self.targetList = $("<ul/>")
					.addClass(self.options.listClass)
					.addClass(self.options.targetListClass)
					.delegate("li", "click", { pickList: self }, self._changeHandler);

			container
					.append(label)
					.append(self.targetList);

			return container;
		},

		_buildControls: function()
		{
			var self = this;

			self.controls = $("<div/>").addClass(self.options.controlsContainerClass);

			self.addAllButton = $("<button type='button'/>").click({pickList: self}, self._addAllHandler).html(self.options.addAllLabel).addClass(self.options.addAllClass);
			self.addButton = $("<button type='button'/>").click({pickList: self}, self._addHandler).html(self.options.addLabel).addClass(self.options.addClass);
			self.removeButton = $("<button type='button'/>").click({pickList: self}, self._removeHandler).html(self.options.removeLabel).addClass(self.options.removeClass);
			self.removeAllButton = $("<button type='button'/>").click({pickList: self}, self._removeAllHandler).html(self.options.removeAllLabel).addClass(self.options.removeAllClass);

			self.controls
					.append(self.addAllButton)
					.append(self.addButton)
					.append(self.removeButton)
					.append(self.removeAllButton);

			return self.controls;
		},

		_populateLists: function()
		{
			var self = this;

			self._trigger("beforePopulate");

			self.element.children().each(function()
			{
				var text = $(this).text();
				var copy = $("<li/>")
						.text(text)
						.attr("label", text)
						.attr(self.options.listItemValueAttribute, $(this).val())
						.addClass(self.options.listItemClass);

				if($(this).attr("selected") == "selected")
				{
					self.targetList.append( copy );
				}
				else
				{
					self.sourceList.append( copy );
				}
			});

			self.insertItems(self.options.items);

			self._trigger("afterPopulate");
		},

		_addAllHandler: function(e)
		{
			var self = e.data.pickList;

			self._trigger("beforeAddAll");

			var items = self.sourceList.children();
			self.targetList.append( self._removeSelections(items) );

			items.each(function()
			{
				self.element.children("[value='" + self._getItemValue(this) + "']").attr("selected", "selected");
			});

			self._refresh();

			self._trigger("afterAddAll");
		},

		_addHandler: function(e)
		{
			var self = e.data.pickList;

			self._trigger("beforeAdd");

			var items = self.sourceList.children(".ui-selected");
			self.targetList.append( self._removeSelections(items) );

			items.each(function()
			{
				self.element.children("[value='" + self._getItemValue(this) + "']").attr("selected", "selected");
			});

			self._refresh();

			self._trigger("afterAdd");
		},

		_removeHandler: function(e)
		{
			var self = e.data.pickList;

			self._trigger("beforeRemove");

			var items = self.targetList.children(".ui-selected");
			self.sourceList.append( self._removeSelections(items) );

			items.each(function()
			{
				self.element.children("[value='" + self._getItemValue(this) + "']").removeAttr("selected");
			});

			self._refresh();

			self._trigger("afterRemove");
		},

		_removeAllHandler: function(e)
		{
			var self = e.data.pickList;

			self._trigger("beforeRemoveAll");

			var items = self.targetList.children();
			self.sourceList.append( self._removeSelections(items) );

			items.each(function()
			{
				self.element.children("[value='" + self._getItemValue(this) + "']").removeAttr("selected");
			});

			self._refresh();

			self._trigger("afterRemoveAll");
		},

		_refresh: function()
		{
			var self = this;

			self._trigger("beforeRefresh");

			self._refreshControls();

			// Sort the selection lists.
			if(self.options.sortItems)
			{
				self._sortItems(self.sourceList, self.options);
				self._sortItems(self.targetList, self.options);
			}

			self._trigger("afterRefresh");
		},

		_refreshControls: function()
		{
			var self = this;

			self._trigger("beforeRefreshControls");

			// Enable/disable the Add All button state.
			if(self.sourceList.children().length)
			{
				self.addAllButton.removeAttr("disabled");
				self.addAllButton.removeClass('ui-button-disabled ui-state-disabled')
			}
			else
			{
				self.addAllButton.attr("disabled", "disabled");
				self.addAllButton.addClass('ui-button-disabled ui-state-disabled')
			}

			// Enable/disable the Remove All button state.
			if(self.targetList.children().length)
			{
				self.removeAllButton.removeAttr("disabled");
				self.removeAllButton.removeClass('ui-button-disabled ui-state-disabled')
			}
			else
			{
				self.removeAllButton.attr("disabled", "disabled");
				self.removeAllButton.addClass('ui-button-disabled ui-state-disabled')
			}

			// Enable/disable the Add button state.
			if(self.sourceList.children(".ui-selected").length)
			{
				self.addButton.removeAttr("disabled");
				self.addButton.removeClass('ui-button-disabled ui-state-disabled')
			}
			else
			{
				self.addButton.attr("disabled", "disabled");
				self.addButton.addClass('ui-button-disabled ui-state-disabled')
			}

			// Enable/disable the Remove button state.
			if(self.targetList.children(".ui-selected").length)
			{
				self.removeButton.removeAttr("disabled");
				self.removeButton.removeClass('ui-button-disabled ui-state-disabled')
			}
			else
			{
				self.removeButton.attr("disabled", "disabled");
				self.removeButton.addClass('ui-button-disabled ui-state-disabled')
			}

			self._trigger("afterRefreshControls");
		},

		_sortItems: function(list, options)
		{
			var items = new Array();

			list.children().each(function()
			{
				items.push( $(this) );
			});

			items.sort(function(a, b)
			{
				if(a.attr(options.sortAttribute) > b.attr(options.sortAttribute))
				{
					return 1;
				}
				else if(a.attr(options.sortAttribute) == b.attr(options.sortAttribute))
				{
					return 0;
				}
				else
				{
					return -1;
				}
			});

			list.empty();

			for(var i = 0; i < items.length; i++)
			{
				list.append(items[i]);
			}
		},

		_changeHandler: function(e)
		{
			var self = e.data.pickList;

			if(e.ctrlKey)
			{
				if(self._isSelected( $(this) ))
				{
					self._removeSelection( $(this) );
				}
				else
				{
					self.lastSelectedItem = $(this);
					self._addSelection( $(this) );
				}
			}
			else if(e.shiftKey)
			{
				var current = self._getItemValue(this);
				var last = self._getItemValue(self.lastSelectedItem);

				if($(this).index() < $(self.lastSelectedItem).index())
				{
					var temp = current;
					current = last;
					last = temp;
				}

				var pastStart = false;
				var beforeEnd = true;

				self._clearSelections( $(this).parent() );

				$(this).parent().children().each(function()
				{
					if(self._getItemValue(this) == last)
					{
						pastStart = true;
					}

					if(pastStart && beforeEnd)
					{
						self._addSelection( $(this) );
					}

					if(self._getItemValue(this) == current)
					{
						beforeEnd = false;
					}

				});
			}
			else
			{
				self.lastSelectedItem = $(this);
				self._clearSelections( $(this).parent() );
				self._addSelection( $(this) );
			}

			self._refreshControls();
		},

		_isSelected: function(listItem)
		{
			return listItem.hasClass("ui-selected");
		},

		_addSelection: function(listItem)
		{
			var self = this;

			return listItem
					.addClass("ui-selected")
					.addClass("ui-state-highlight")
					.addClass(self.options.selectedListItemClass);
		},

		_removeSelection: function(listItem)
		{
			var self = this;

			return listItem
					.removeClass("ui-selected")
					.removeClass("ui-state-highlight")
					.removeClass(self.options.selectedListItemClass);
		},

		_removeSelections: function(listItems)
		{
			var self = this;

			listItems.each(function()
			{
				$(this)
						.removeClass("ui-selected")
						.removeClass("ui-state-highlight")
						.removeClass(self.options.selectedListItemClass);
			});

			return listItems;
		},

		_clearSelections: function(list)
		{
			var self = this;

			list.children().each(function()
			{
				self._removeSelection( $(this) );
			});
		},

		_setOption: function(key, value)
		{
			switch(key)
			{
				case "clear":
				{
					break;
				}
			}

			$.Widget.prototype._setOption.apply(this, arguments);
		},

		destroy: function()
		{
			var self = this;

			self._trigger("onDestroy");

			self.pickList.remove();
			self.element.show();

			$.Widget.prototype.destroy.call(self);
		},

		insert: function(item)
		{
			var self = this;

			var list = item.selected ? self.targetList : self.sourceList;
			var selectItem = self._createSelectItem(item);
			var listItem = (item.element == undefined) ? self._createRegularItem(item) : self._createRichItem(item);

			self.element.append(selectItem);
			list.append(listItem);

			self._refresh();
		},

		insertItems: function(items)
		{
			var self = this;

			var selectItems = [];
			var sourceItems = [];
			var targetItems = [];

			$(items).each(function()
			{
				var selectItem = self._createSelectItem(this);
				var listItem = (this.element == undefined) ? self._createRegularItem(this) : self._createRichItem(this);

				selectItems.push(selectItem);

				if(this.selected)
				{
					targetItems.push(listItem);
				}
				else
				{
					sourceItems.push(listItem);
				}
			});

			self.element.append(selectItems.join("\n"));
			self.sourceList.append(sourceItems.join("\n"));
			self.targetList.append(targetItems.join("\n"));
		},

		_createSelectItem: function(item)
		{
			var selected = item.selected ? " selected='selected'" : "";
			return "<option value='" + item.value + "'" + selected + ">" + item.label + "</option>";
		},

		_createRegularItem: function(item)
		{
			var self = this;
			return "<li " + self.options.listItemValueAttribute + "='" + item.value + "' label='" + item.label + "' class='" + self.options.listItemClass + "'>" + item.label + "</li>";
		},

		_createRichItem: function(item)
		{
			var self = this;

			var richItemHtml = item.element.clone().wrap("<div>").parent().html();
			item.element.hide();

			return "<li " + self.options.listItemValueAttribute + "='" + item.value + "' label='" + item.label + "' class='" + self.options.listItemClass + " " + self.options.richListItemClass + "'>" + richItemHtml + "</li>";
		},

		_getItemValue: function(item)
		{
			var self = this;
			return $(item).attr(self.options.listItemValueAttribute);
		}
	});
}(jQuery));