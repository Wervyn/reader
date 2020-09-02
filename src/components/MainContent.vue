<template>
    <div class="container">
        <h2 class="justify-content-center">
            <a v-if="chapter.titlelink" :href="chapter.titlelink" target="_blank">{{ chapter.title }}</a>
            <a v-else>{{ chapter.title }}</a>
        </h2>
        <div v-for="(line, index) in chapter.content" :key="'line'+index">
            <p v-if="!!line && line != '---' && line.slice(0,4) != 'img='" class="text-justify">
                <span class="width:15px; overflow:hidden;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                <span v-for="(substr, i) in line.split('__')" :key="'line'+index+'part'+i">
                    <a v-if="substr[0] == '[' && substr.slice(-1) == ']'" class="footnote"
                        :name="`anchor-${substr.slice(1,-1)}`" :href="`#footnote-${substr.slice(1,-1)}`">
                            [{{ substr.slice(1,-1) }}]
                    </a>
                    <a v-else-if="substr[0] == '<' && substr.slice(-1) == '>'" :href="substr.slice(1,-1).split('|')[0]" target="_blank">
                        {{ substr.slice(1,-1).split('|')[1] }}
                    </a>
                    <a v-else :style="{'font-style': i%2 ? 'italic' : 'normal'}">{{ substr }}</a>
                </span>
            </p>
            <br v-if="!line" /><br v-if="!line" />
            <hr v-if="line=='---'" />
            <div v-if="line.slice(0,4) == 'img='" class="image-embed"><img :src="line.slice(4)" /></div>
        </div>
        <hr v-if="chapter.endnotes || chapter.footnotes" />
        <h5 v-if="chapter.endnotes" style="font-style: italic;">Author's Note:</h5>
        <div v-for="(line, index) in chapter.endnotes" :key="'endnote'+index">
            <p v-if="!!line && line != '---' && line.slice(0,4) != 'img='" class="text-justify">
                <span v-for="(substr, i) in line.split('__')" :key="'endnote'+index+'part'+i"
                    :style="{'font-style': i%2 ? 'italic' : 'normal'}">
                    {{ substr }}
                </span>
            </p>
            <br v-if="!line" /><br v-if="!line" />
            <hr v-if="line=='---'" />
            <div v-if="line.slice(0,4) == 'img='" class="image-embed"><img :src="line.slice(4)" /></div>
        </div>
        <br v-if="chapter.endnotes && chapter.footnotes" />
        <h5 v-if="chapter.footnotes" style="font-style: italic;">Translator's Note:</h5>
        <div v-for="(line, index) in chapter.footnotes" :key="'footnote'+index">
            <p v-if="!!line && line != '---' && line.slice(0,4) != 'img='" class="text-justify">
                <a v-if="line.slice(-1) == '^'" class="footnote" :name="`footnote-${index+1}`" :href="`#anchor-${index+1}`">[{{ index + 1 }}]</a>
                <span v-for="(substr, i) in line.slice(0,-1).split('__')" :key="'footnote'+index+'part'+i">
                    <a v-if="substr[0] == '<' && substr.slice(-1) == '>'" :href="substr.slice(1,-1).split('|')[0]" target="_blank">
                        {{ substr.slice(1,-1).split('|')[1] }}
                    </a>
                    <a v-else :style="{'font-style': i%2 ? 'italic' : 'normal'}">{{ substr }}</a>
                </span>
            </p>
            <br v-if="!line" /><br v-if="!line" />
            <hr v-if="line=='---'" />
            <div v-if="line.slice(0,4) == 'img='" class="image-embed"><img :src="line.slice(4)" /></div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        chapter: Object
    }
}
</script>

<style scoped>
    .container {
        padding-top: 10px;
        min-height: 100%;
        max-height: 100%;
        overflow-y: scroll;
        font-family: 'TextFont', Times, sans-serif;
        font-size: 14pt;
    }
    .container > h2 {
        font-family: 'TitleFont', Times, sans-serif;
    }
    .footnote {
        font-size: 10pt;
    }
    .image-embed {
        width: auto;
        text-align: center;
    }
    .image-embed img {
        max-width: 95%;
        height: auto;
    }
</style>