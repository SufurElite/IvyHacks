<template>
  <f7-page name="about">
    <f7-navbar :sliding="false" large>
      <f7-button v-on:click="onLogoutClicked" style="text-align:left; width:100%"> Logout </f7-button>
      <h4 style="text-align:right; width: 100%;">{{this.email}}</h4>
      <f7-nav-title-large sliding style="text-align:center; width: 100%;">Copy Chess</f7-nav-title-large>
    </f7-navbar>
    <f7-block-title style="text-align: center">Watch Bots Play Each Other</f7-block-title>
      <div id="watchapp" style="display: flex;align-items: center;justify-content: center;">
        <f7-row>
          <watchbot :gameStarted="gameStarted"></watchbot>
        </f7-row>
      </div>
      <div>
        <form>
        Player 1: 
      <dropdown :options="usernames" :selected="object" v-on:updateOption="selectMethod" :placeholder="'Trained Model'"></dropdown>
        <br>
        Player 2: 
        <dropdown :options="usernames"  :selected="object" v-on:updateOption="selectMethod2" :placeholder="'Trained Model'"></dropdown>
      <f7-button @click="startGame"> Begin Game </f7-button>
      </form>
    </div>  
    <f7-block>
      <f7-block-header> You are logged in as {{this.email}} </f7-block-header>
      <p>Fugiat perspiciatis excepturi, soluta quod non ullam deleniti. Nobis sint nemo consequuntur, fugiat. Eius perferendis animi autem incidunt vel quod tenetur nostrum, voluptate omnis quasi quidem illum consequuntur, a, quisquam.</p>
      <p>Laudantium neque magnam vitae nemo quam commodi, in cum dolore obcaecati laborum, excepturi harum, optio qui, consequuntur? Obcaecati dolor sequi nesciunt culpa quia perspiciatis, reiciendis ex debitis, ut tenetur alias.</p>
    </f7-block>
    <!-- Tabbar for switching views-tabs -->
    <f7-toolbar tabbar labels bottom>
      <f7-link @click="toPlay" icon-md="material:games" text="Play"></f7-link>
      <f7-link @click="toTrain" icon-md="material:code" text="Train"></f7-link>
      <f7-link link="#" tab-link-active icon-md="material:tv" text="Watch"></f7-link>
    </f7-toolbar>
  </f7-page>
</template>
<script>
import routes from '../js/routes.js';
import * as firebase from 'firebase';
import {chessboard} from 'vue-chessboard'
import 'vue-chessboard/dist/vue-chessboard.css'
import watchbot from "./watchbot.vue"
import { db } from '../js/app';
import { firebaseApp } from '../js/app';
import dropdown from 'vue-dropdowns'
import 'firebase/auth';

export default {
  name: "watchapp",
  components: {
    chessboard,
    watchbot,
  },
  data() {
      return {
        user: true,
        email: firebase.auth().currentUser.email,
        usernames: [],
        object: {
          name: 'Lichess Username',
        },
        gameStarted: false
      };
    },
  firestore() {
    return{
    usernames: db.collection("usernames").where("email", "==", this.email)
    }
  },
    components: {
            'dropdown': dropdown,
            'chessboard': chessboard,
            'watchbot': watchbot
  },
  methods: {
      onLogoutClicked() {
        firebase.auth().signOut().catch((error) =>{
          console.error("Error when trying to logout user", error);
        });  
        this.$f7.views.main.router.navigate('/');
      },
      startGame(){
        if(this.$root.bot=='' || this.$root.bot2==''){
          this.$f7.dialog.alert('Please select both bots before playing.');
        } else {
          console.log(this.$root.bot)
          console.log(this.$root.bot2)
          this.gameStarted = true;
          if(this.color=="white"){
            console.log(this.$root.bot)
            console.log(this.$root.ComputerColor)
            console.log(this.$root.fen)
          } else {
            
          }
        }
      },
      toTrain(){
        this.$f7.views.main.router.navigate('/home/');
        this.$root.ComputerColor = "black";
        this.$root.bot = "";
        this.$root.bot2 = "";
        this.$root.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
        this.gameStarted = false;
      },
      toPlay(){
        this.$f7.views.main.router.navigate('/play/');
        this.$root.ComputerColor = "black";
        this.$root.bot = "";
        this.$root.bot2 = "";
        this.$root.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
        this.gameStarted = false;
      },
      showInfo(data) {
      this.positionInfo = data
      },
      loadFen(fen) {
        this.currentFen = fen
      },
      promote() {
        if (confirm("Want to promote to rook? Queen by default") ) {
          return 'r'
        } else {
          return 'q'
        }
      },
      selectMethod(payload){
        this.object.name = payload.username;
        this.$root.bot = payload.username;
      },
      selectMethod2(payload){
        this.object.name = payload.username;
        this.$root.bot2 = payload.username;
      }
  }
}
</script>