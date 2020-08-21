<template>
  <div class="container" id="app">
    <div class="top-bar row justify-content-center"><div class="col">
      <h1 v-if="topnav.title" class="title">{{ topnav.title }}</h1>
      <h4 v-if="topnav.subtitle" class="subtitle">{{ topnav.subtitle }}</h4>
    </div></div>
    <div class="row">
      <div class="col-sm-3 center home-link">
        <router-link to="/reader" class="col-sm=3 justify-content-center nav-link">Home</router-link>
      </div>
      <top-nav class="col-9" :books="topnav.books" :active="bookNumber" />
    </div>
    <div class="row">
      <side-nav class="col-sm-3" :book="book" :bookNumber="bookNumber" :active="chapterNumber" />
      <main-content class="col-9" :chapter="chapter" ref="mainContent" />
    </div>
  </div>
</template>

<script>
import { reactive, toRefs, onMounted } from 'vue'

import TopNav from './TopNav.vue'
import SideNav from './SideNav'
import MainContent from './MainContent.vue'

let datapath = "/wervyn/honzuki/data/";

export default {
  name: 'Wrapper',
  props: {
    bookNumber: {default: -1},
    chapterNumber: {default: -1}
  },
  components: {
    TopNav,
    SideNav,
    MainContent
  },
  watch: {
    '$route': async function (to, from) {
        if (to.path == from.path) {
          console.log("route aborted: " + to.path);
          return
        }
        let tempfetch = await fetch(`${datapath}topnav.json`);
        this.topnav = await tempfetch.json();

        let bookpath = `${datapath}updates/__nav.json`
        if (this.bookNumber >= 0) {
          bookpath = `${datapath}${this.topnav.books[this.bookNumber].content}`;
        }
        tempfetch = await fetch(bookpath);
        this.book = await tempfetch.json();

        let chapterpath = `${datapath}landing.json`;
        if (this.chapterNumber < 0) {
          if (this.book.default) chapterpath = `${datapath}${this.book.default}`;
        } else {
          chapterpath = `${datapath}${this.book.chapters[this.chapterNumber].content}`;
        }
        tempfetch = await fetch(chapterpath);
        this.chapter = await tempfetch.json();
        this.$refs.mainContent.$el.scrollTop = 0;
    }
  },
  setup(props) {
    const data = reactive({
      topnav: {},
      book: {},
      chapter: {}
    });

    onMounted(async () => {
        let tempfetch = await fetch(`${datapath}topnav.json`);
        data.topnav = await tempfetch.json();

        let bookpath = `${datapath}updates/__nav.json`
        if (props.bookNumber >= 0) {
          bookpath = `${datapath}${data.topnav.books[props.bookNumber].content}`;
        }
        tempfetch = await fetch(bookpath);
        data.book = await tempfetch.json();

        let chapterpath = `${datapath}landing.json`;
        if (props.chapterNumber < 0) {
          if (data.book.default) chapterpath = `${datapath}${data.book.default}`;
        } else {
          chapterpath = `${datapath}${data.book.chapters[props.chapterNumber].content}`;
        }
        tempfetch = await fetch(chapterpath);
        data.chapter = await tempfetch.json();
    });

    return {...toRefs(data)};
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
.top-bar {
  padding-top: 20px;
  background-color: #6cf;
  color: #22b;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;  
  background-image: url(/wervyn/honzuki/crest.png);
  background-position: 20px 20px;
  background-size: 100px 72px;
  background-repeat: no-repeat;
}
.title {
  font-family: 'TitleFont', Times, serif;
}
.subtitle {
  font-family: 'TextFont', Times, serif;
}
.home-link {
  background-color: #8df;
  border-bottom: 3px solid #22b;
  font-size: 20px;
}
</style>