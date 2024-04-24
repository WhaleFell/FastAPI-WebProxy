// A simple authorization module base on `localStorage` in browser
// NOTE: DONT use this in production, it's not exactly secure.

// ref:
// https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage
// crypto-js: https://github.com/brix/crypto-js
// https://cryptojs.gitbook.io/docs

import CryptoJS from 'crypto-js'


interface UserDB {
    username: string
    // md5("password" + salt)
    password_md5: string
}

interface StoreUser {
    user: string
    epwd: string
}

interface AuthObj {
    login(username: string, password: string): boolean
    logout(username: string): void
    isLogined(): boolean
}


export class Auth implements AuthObj {
    private userDBs: UserDB[]
    // md5 salt for password. This value must be changed randomly.
    private salt: string
    private expire: number
    private localStoreField = "auth"

    constructor(userDBs: UserDB[], salt: string = "hyy", expire: number = 5) {
        this.userDBs = userDBs
        this.salt = salt
        this.expire = expire
    }

    sha256AndBase64(text: string): string {
        return CryptoJS.SHA256(text).toString(CryptoJS.enc.Base64)
    }

    private prepareEncrypt(text: string): string {
        return CryptoJS.MD5(text + this.salt).toString()
    }

    private expireSalt(expire: number): string {
        let now = new Date()
        // get seconds timestamp
        let timestamp: number = Math.floor(now.getTime() / 1000)
        return Math.floor(timestamp / (expire * 60)).toString()

    }

    private customEncrypt(text: string): string {
        // const start: number = new Date().getTime() // ms
        // const start = performance.now();
        const steps: number = 8
        let encryptRes: string | null = null
        for (let i = 0; i <= steps; i++) {
            if (!encryptRes) {
                encryptRes = this.sha256AndBase64(text + this.salt + this.expireSalt(this.expire))
            } else {
                encryptRes = this.sha256AndBase64(encryptRes + this.salt.repeat(2) + this.expireSalt(this.expire))
            }
        }
        // Timer - Calculate encrypt time
        // const end: number = new Date().getTime()
        // const end = performance.now();
        // console.log(`Encrypt time: ${end - start}ms`)
        return encryptRes as string
    }

    authenticate(user: StoreUser): boolean {
        let [foundedUser] = this.userDBs.filter((value: UserDB) => value.username === user.user)
        if (!foundedUser) return false

        let epwd: string = this.customEncrypt(foundedUser.password_md5)

        if (epwd === user.epwd) {
            return true
        }
        return false
    }

    login(username: string, password: string): boolean {
        // Do md5 for password first.
        password = this.prepareEncrypt(password)

        let [foundedUser] = this.userDBs.filter((value: UserDB) => value.username === username)
        if (!foundedUser) return false

        let epwd: string = this.customEncrypt(foundedUser.password_md5)

        if (epwd === this.customEncrypt(password)) {
            let storeUser: StoreUser = {
                user: username,
                epwd: epwd
            }
            localStorage.setItem(this.localStoreField, JSON.stringify(storeUser))
            return true
        }
        return false
    }

    logout(): void {
        localStorage.removeItem(this.localStoreField)
    }

    isLogined(): boolean {
        const existUser = localStorage.getItem(this.localStoreField)
        if (!existUser) {
            return false
        }

        let obj: StoreUser = JSON.parse(existUser) as StoreUser
        return this.authenticate(obj)

    }
}

const userDBs: UserDB[] = [
    {
        username: 'admin',
        // lovehyy
        password_md5: '7788a820ccc6b5208c2958edee01f32e'
    },

]

export const auth = new Auth(userDBs, "hyyLover8964", 60)
