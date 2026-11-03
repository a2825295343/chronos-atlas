import texts from './localization/text.zh.json';
const dictionary=texts as Record<string,string>;
export function zhText(value:string|number|undefined|null){const text=String(value??'');return dictionary[text]||text;}
