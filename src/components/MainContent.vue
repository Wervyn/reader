<template>
    <div class="container">
        <div class="main-content" ref="mainPanel">
            <h2 class="justify-content-center">
                <a v-if="chapter.titlelink" :href="chapter.titlelink" target="_blank">{{ chapter.title }}</a>
                <a v-else>{{ chapter.title }}</a>
            </h2>
            <div v-for="(line, index) in chapter.content" :key="'line'+index">
                <p v-if="!!line && line != '---' && line.slice(0,4) != 'img='" class="text-justify">
                    <span class="width:15px; overflow:hidden;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                    <span v-for="(substr, i) in line.split('__')" :key="'line'+index+'part'+i">
                        <a v-if="substr == '*'" class="footnote"
                            :name="`anchor-${anchor(index, i)}`" :href="`#footnote-${anchor(index, i)}`">
                                [{{ anchor(index, i) }}]
                        </a>
                        <a v-else-if="substr[0] == '<' && substr.slice(-1) == '>'" :href="substr.slice(1,-1).split('|')[0]" target="_blank">
                            {{ substr.slice(1,-1).split('|')[1] }}
                        </a>
                        <a v-else-if="substr.slice(0,2) == '**' && substr.slice(-2) == '**'" style="font-style: italic; font-weight: bold;">{{ substr.slice(2, -2) }}</a>
                        <a v-else-if="substr[0] == '*' && substr.slice(-1) == '*'" style="font-weight: bold;">{{ substr.slice(1, -1) }}</a>
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
                    <a v-if="line.slice(-1) == '^'" class="footnote" :name="`footnote-${footnote(index)}`" :href="`#anchor-${footnote(index)}`">[{{ footnote(index) }}]&nbsp;</a>
                    <span v-for="(substr, i) in line.slice(0,-1).split('__')" :key="'footnote'+index+'part'+i">
                        <a v-if="substr[0] == '<' && substr.slice(-1) == '>'" :href="substr.slice(1,-1).split('|')[0]" target="_blank">
                            {{ substr.slice(1,-1).split('|')[1] }}
                        </a>
                        <a v-else-if="substr.slice(0,2) == '**' && substr.slice(-2) == '**'" style="font-style: italic; font-weight: bold;">{{ substr.slice(2, -2) }}</a>
                        <a v-else-if="substr[0] == '*' && substr.slice(-1) == '*'" style="font-weight: bold;">{{ substr.slice(1, -1) }}</a>
                        <a v-else :style="{'font-style': i%2 ? 'italic' : 'normal'}">{{ substr }}</a>
                    </span>
                </p>
                <br v-if="!line" /><br v-if="!line" />
                <hr v-if="line=='---'" />
                <div v-if="line.slice(0,4) == 'img='" class="image-embed"><img :src="line.slice(4)" /></div>
            </div>
        </div>
        <footer-nav class="footer-nav" :book="bookNumber" :index="chapterNumber" :max="totalChapters - 1" />
    </div>
</template>

<script>
import FooterNav from './FooterNav.vue'

export default {
    components: { FooterNav },
    props: {
        chapter: Object,
        bookNumber: Number,
        chapterNumber: Number,
        totalChapters: Number
    },
    created() {
        this.anchorDict = {},
        this.footnoteDict = {};
    },
    watch: {
        'chapterNumber': function() {
            this.anchorDict = {},
            this.footnoteDict = {}
        }
    },
    methods: {
        anchor(index, pos) {
            if (!this.anchorDict[index*1000+pos]) {
                this.anchorDict[index*1000+pos] = Object.keys(this.anchorDict).length + 1;
            }
            return this.anchorDict[index*1000+pos];
        },
        footnote(index) {
            if (!this.footnoteDict[index]) {
                this.footnoteDict[index] = Object.keys(this.footnoteDict).length + 1;
            }
            return this.footnoteDict[index];
        },
        scrollToTop() {
            this.$refs.mainPanel.scrollTop = 0;
        }
    }
}
</script>

<style scoped>
    .container {
        min-height: 100%;
        max-height: 100%;
        padding: 0;
    }
    .main-content {
        padding: 15px;
        padding-top: 10px;
        min-height: calc(100% - 40px);
        max-height: calc(100% - 40px);
        overflow-y: scroll;
        font-family: 'TextFont', Times, sans-serif;
        font-size: 14pt;
    }
    .main-content > h2 {
        font-family: 'TitleFont', Times, sans-serif;
    }
    .footer-nav {
        height: 40px;
        min-height: 40px;
        max-height: 40px;
    }
    .footnote {
        font-size: 10pt;
        font-weight: bold;
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