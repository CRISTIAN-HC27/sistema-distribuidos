module.exports = {
    apps: [
        {
            name: 'backend-5001',
            script: './backend/server.js',
            env: {
                PORT: 5001,
            }
        },
        {
            name: 'backend-5002',
            script: './backend/server.js',
            env: {
                PORT: 5002,
            }
        }
    ]
}