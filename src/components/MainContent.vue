<template>
    <div class="container">
        <div class="main-content" :class="isDark()" ref="mainPanel">
            <vue-audio v-if="chapter.audio" :file="`/wervyn/honzuki/data/${chapter.audio}`" />
            <br v-if="chapter.audio" />
            <h2 class="justify-content-center">
                <a v-if="chapter.titlelink" :href="chapter.titlelink" target="_blank">{{ hideSpoilers() && chapter.spoilerTitle ? chapter.spoilerTitle : chapter.title }}</a>
                <a v-else>{{ hideSpoilers() && chapter.spoilerTitle ? chapter.spoilerTitle : chapter.title }}</a>
            </h2>
            <div v-if="chapter.metadata" class="info">
                <div v-for="(value, key, index) in chapter.metadata" class="info-line" :key="'info'+index"><strong>{{ key }}:</strong> {{ value }} </div>
            </div>
            <div v-for="(line, index) in chapter.content" :key="'line'+index">
                <p v-if="!!line && line != '---' && line.slice(0,4) != 'img='" class="text-justify">
                    <span class="spacer"></span>
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
                        <a v-else-if="substr[0] == '~' && substr.slice(-1) == '~'" style="text-decoration: line-through;">{{ substr.slice(1, -1) }}</a>
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
                        <a v-else-if="substr[0] == '~' && substr.slice(-1) == '~'" style="text-decoration: line-through;">{{ substr.slice(1, -1) }}</a>
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
import VueAudio from 'vue-audio'

export default {
    components: { FooterNav, VueAudio },
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
        isDark() {
            return localStorage.getItem("isDark") ? "dark" : "";
        },
        hideSpoilers() {
            return localStorage.getItem("hideSpoilers") ? true : false;
        },
        scrollToTop() {
            this.$refs.mainPanel.scrollTop = 0;
            if (this.chapterNumber != -1) {
                this.$refs.mainPanel.scrollIntoView({
                    behavior: 'smooth'
                });
            }
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
        font-family: 'TextFont', Times, serif;
        font-size: 14pt;
    }
    .main-content > h2 {
        font-family: 'TitleFont', Times, serif;
    }
    .main-content.dark {
        background-color: #333;
        color: #ccc;
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
        max-height: 600px;
        max-width: 95%;
    }
    .info {
        text-align: right;
        font-family: 'TextFont', Times, serif;
        color: rgb(173, 140, 140);
        font-size: 10pt;
    }
    .info-line {
        display: inline-block;
        padding-left: 10px;
    }
    .spacer {
        min-width: 20px;
        min-height: 15px;
        max-width:20px;
        max-height:15px;
        display: inline-block;
    }
</style>