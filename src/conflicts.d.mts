export function warsAtYear(database:any,details:any,year:number):any[];
export function participantsAt(war:any,year:number):any[];
export function inPeriods(periods:number[][],year:number):boolean;
export function inferredCause(war:any,year:number):string;
export const outcomeNames:Record<number,string>;
export function interpolateStrength(observations:any,year:number):{value:number;estimated:boolean;years:number[]}|null;
