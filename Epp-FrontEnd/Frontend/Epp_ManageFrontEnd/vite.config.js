import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
    base: '/manage/',
    plugins: [
        vue(),
        AutoImport({
            resolvers: [
                // 自动导入图标组件
                IconsResolver({
                    prefix: 'Icon'
                }),
                ElementPlusResolver()
            ]
        }),
        Components({
            resolvers: [
                // 自动注册图标组件
                IconsResolver({
                    enabledCollections: ['ep']
                }),
                ElementPlusResolver()
            ]
        }),
        Icons({
            autoInstall: true
        }),
        nodePolyfills({
            // 显式启用 crypto 模块的 polyfill
            globals: { crypto: true }
        })
    ],

    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    }
})
