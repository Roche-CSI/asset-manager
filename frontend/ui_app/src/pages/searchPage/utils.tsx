/**
 * Converts a given string to sentence case.
 * @param text - The string to be converted.
 * @returns The sentence-cased string.
 */
export function toSentenceCase(text: string): string {
	if (!text) return text; // Return early if the input is an empty string or null
	
	// Convert the first character to uppercase and the rest to lowercase
	return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

/**
 * Converts a given string to title case.
 * @param text - The string to be converted.
 * @returns The title-cased string.
 */
export function toTitleCase(text: string): string {
	if (!text) return text; // Return early if the input is an empty string or null
	
	// Define words that should be lowercase unless they are the first or last word
	const lowerCaseWords = new Set(['and', 'or', 'but', 'the', 'a', 'an', 'of', 'in', 'to', 'with']);
	
	// Capitalize the first and last words and words not in the lowercase set
	return text
		.split(' ')
		.map((word, index, array) => {
			// Capitalize first and last words or words not in the lowercase set
			if (index === 0 || index === array.length - 1 || !lowerCaseWords.has(word.toLowerCase())) {
				return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
			}
			return word.toLowerCase();
		})
		.join(' ');
}
