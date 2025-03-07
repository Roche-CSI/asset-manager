// Interface for the `taggables` table
export interface Tag {
	name: string;
	label: string;
}

export interface TagCategory {
	name: string;
	label: string;
	tags: Tag[];
}

export interface TagGroup {
	name: string;
	label: string;
	categories: TagCategory[];
}

export default class Taggable {
	// Create a default taggable object
	
	static defaultTagGroup({name = "default", label = "Default", category}: {
		name?: string;
		label?: string;
		category: TagCategory
	}): TagGroup {
		// Create a tag group with a single category
		return {
			name,
			label,
			categories: [category]
		};
	}
	
	static defaultTagCategory(
		{
			name = "default",
			label = "Default",
			tags = [],
			tagFormatter = (tag: string) => tag.split('.')[0]
		}:
			{
				name?: string;
				label?: string;
				tags?: string[],
				tagFormatter?: (tag: string) => string;
			}): TagCategory {
		return {
			name,
			label,
			tags: tags.map(tag => ({name: tag, label: tagFormatter(tag)}))
		};
	}
	
	static highlightKeysForGroup(tagGroup): string[] {
		return tagGroup.categories.flatMap(category => Object.keys(category.selected || {}));
	}
}
