export enum ContactState {
    online,
    offline,
    undetermined
}

export interface Contact {
    contact_id: string
    name: string
    approved: boolean
    awaiting_approval: boolean
    address: string
    online: ContactState
}