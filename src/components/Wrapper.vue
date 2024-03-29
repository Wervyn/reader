<template>
  <div class="container" id="app">
    <div ref="topBar">
      <div class="top-bar row justify-content-center"><div class="col">
        <h1 v-if="topnav.title" class="title">{{ topnav.title }}</h1>
        <h4 v-if="topnav.subtitle" class="subtitle">{{ topnav.subtitle }}</h4>
        <div class="darkButton" @click="toggleDarkMode()">{{ isDark() ? "Light Mode" : "Dark Mode" }}</div>
        <div class="spoilerButton" @click="toggleSpoilers()">{{ hideSpoilers() ? "Show Spoilers" : "Low Spoilers" }}</div>
      </div></div>
      <div class="row">
        <div class="col-sm-3 center-text home-link">
          <router-link to="/reader" class="justify-content-center nav-link">Home</router-link>
        </div>
        <top-nav class="col-sm-9 justify-content-center" :books="topnav.books" :active="bookNumber" />
      </div>
    </div>
    <div class="row main-flex" :style="{'max-height': `calc(100vh - ${finalTopHeight})`, 'height': `calc(100vh - ${finalTopHeight})`}">
      <side-nav class="col-sm-3" :book="book" :bookNumber="bookNumber" :active="chapterNumber" ref="sideNav" :key="rerender" />
      <main-content class="col-sm-9 justify-content-center" :chapter="chapter" :chapterNumber="+chapterNumber"
        :bookNumber="+bookNumber" :totalChapters="book?.chapters?.length ?? 1" ref="mainContent" :key="rerender" />
    </div>
  </div>
</template>

<script>
import { reactive, ref, toRefs, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

import TopNav from './TopNav.vue'
import SideNav from './SideNav.vue'
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
  computed: {
    finalTopHeight() {
      return this.topHeight ? this.topHeight + 'px' : '25vh'
    }
  },
  methods: {
    isDark() {
      return localStorage.getItem("isDark") ? true : false;
    },
    toggleDarkMode() {
      if (this.isDark()) {
        localStorage.removeItem("isDark");
        document.body.className = "";
      } else {
        localStorage.setItem("isDark", "true");
        document.body.className = "dark";
      }
      this.rerender++;
    },
    hideSpoilers() {
      return localStorage.getItem("hideSpoilers") ? true : false;
    },
    toggleSpoilers() {
      if (this.hideSpoilers()) {
        localStorage.removeItem("hideSpoilers");
      } else {
        localStorage.setItem("hideSpoilers", true);
      }
      this.rerender++;
    }
  },
  watch: {
    '$route': async function (to, from) {
        if (to.path == from.path) {
          console.log("route aborted: " + to.path);
          return
        }
        let tempfetch = await fetch(`${datapath}topnav.json`, {cache: "no-cache"});
        this.topnav = await tempfetch.json();

        let bookpath = `${datapath}updates-nav.json`
        if (this.bookNumber >= 0) {
          bookpath = `${datapath}${this.topnav.books[this.bookNumber].content}`;
          localStorage.setItem("lastBook", this.bookNumber);
        } else {
          localStorage.removeItem("lastBook");
        }
        tempfetch = await fetch(bookpath, {cache: "no-cache"});
        this.book = await tempfetch.json();

        let chapterpath = `${datapath}landing.json`;
        if (this.chapterNumber < 0) {
          if (this.book.default) chapterpath = `${datapath}${this.book.default}`;
          localStorage.removeItem("lastChapter");
        } else {
          chapterpath = `${datapath}${this.book.dir ? this.book.dir + '/' : ''}${this.book.chapters[this.chapterNumber].content}`;
          localStorage.setItem("lastChapter", this.chapterNumber);
        }
        tempfetch = await fetch(chapterpath, {cache: "no-cache"})
          .then(async response => {
            if (response.status === 401) {
              tempfetch = await fetch(`${datapath}forbidden.json`);
              this.chapter = await tempfetch.json();
            } else {
              this.chapter = await response.json();
            }
            this.$refs.mainContent.scrollToTop();
            this.$refs.sideNav.setTitleHeight();
            this.$refs.sideNav.scrollTo(this.chapterNumber);
          });
    }
  },
  setup(props) {
    const data = reactive({
      topnav: {},
      book: {},
      chapter: {},
      topHeight: 0,
      rerender: 0
    });

    const topBar = ref(null);
    const router = useRouter();

    function setTopHeight() {
      data.topHeight = topBar.value ? topBar.value.clientHeight : 0;
    }

    onMounted(async () => {
        if (props.bookNumber < 0 && props.chapterNumber < 0) {
          if (localStorage.getItem("lastBook")) {
            if (localStorage.getItem("lastChapter")) {
              router.push(`/reader/${localStorage.getItem("lastBook")}/${localStorage.getItem("lastChapter")}`);
            } else {
              router.push(`/reader/${localStorage.getItem("lastBook")}`);
            }
          } else if (localStorage.getItem("lastChapter")) {
            router.push(`/reader/-1/${localStorage.getItem("lastChapter")}`);
          }
        }

        window.addEventListener('resize', setTopHeight);
        setTimeout(setTopHeight, 500);
        document.body.className = localStorage.getItem("isDark") ? "dark" : "";

        let tempfetch = await fetch(`${datapath}topnav.json`, {cache: "no-cache"});
        data.topnav = await tempfetch.json();

        let bookpath = `${datapath}updates-nav.json`
        if (props.bookNumber >= 0) {
          bookpath = `${datapath}${data.topnav.books[props.bookNumber].content}`;
        }
        tempfetch = await fetch(bookpath, {cache: "no-cache"});
        data.book = await tempfetch.json();

        let chapterpath = `${datapath}landing.json`;
        if (props.chapterNumber < 0) {
          if (data.book.default) chapterpath = `${datapath}${data.book.default}`;
        } else {
          chapterpath = `${datapath}${data.book.dir ? data.book.dir + '/' : ''}${data.book.chapters[props.chapterNumber].content}`;
        }
        tempfetch = await fetch(chapterpath, {cache: "no-cache"})
          .then(async response => {
            if (response.status === 401) {
              tempfetch = await fetch(`${datapath}forbidden.json`);
              data.chapter = await tempfetch.json();
            } else {
              data.chapter = await response.json();
            }
          });
    });

    onBeforeUnmount(() => {
        window.removeEventListener('resize', setTopHeight);
    });

    return {...toRefs(data), topBar};
  }
}
</script>

<style>
body.dark {
  background-color: #333;
}
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
.main-flex {
  min-height: 75vh;
  display: flex;
}

.darkButton {
  position: absolute;
  top: -5px;
  right: 15px;
  cursor: pointer;
  border-radius: 10px;
  background-color: #22b;
  color: #fff;
  padding: 10px;
  opacity: 0.5;
}
.darkButton:hover {
  opacity: 1;
}
.spoilerButton {
  position: absolute;
  top: 40px;
  right: 15px;
  cursor: pointer;
  border-radius: 10px;
  background-color: #22b;
  color: #fff;
  padding: 10px;
  opacity: 0.5;
}
.spoilerButton:hover {
  opacity: 1;
}

@media only screen and (max-width: 575px) {
  .main-flex {
    min-height: 90vh;
  }
}
</style>
