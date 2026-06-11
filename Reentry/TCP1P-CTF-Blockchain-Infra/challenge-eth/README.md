# EchoVault

Difficulty: Easy - Medium

EchoVault adalah vault sederhana yang dibuat developer baru di dunia DeFi. User dapat deposit dan withdraw ETH kapan saja.

Developer yakin vault ini aman karena setiap withdraw dicek menggunakan balance internal user. Namun, ada kesalahan kecil pada urutan logic withdraw.

Objective: drain EchoVault sampai balance-nya kurang dari 0.1 ETH, lalu panggil `getFlag()`.

## Hints

1. Perhatikan urutan operasi di `withdraw()`.
2. External call ke `msg.sender` bisa mengeksekusi kode milik contract penerima.
3. `receive()` bisa digunakan untuk memanggil `withdraw()` lagi.
4. Jangan exploit menggunakan EOA biasa. Gunakan contract attacker.
