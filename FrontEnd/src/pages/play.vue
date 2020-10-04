<template>
  <f7-page name="about">
    <f7-navbar :sliding="false" large>
      <f7-button v-on:click="onLogoutClicked" style="text-align:left; width:100%"> Logout </f7-button>
      <h4 style="text-align:right; width: 100%;">{{this.email}}</h4>
      <f7-nav-title-large sliding style="text-align:center; width: 100%;">Copy Chess</f7-nav-title-large>
    </f7-navbar>
    
    <div id="chessapp" style="display: flex;align-items: center;justify-content: center;">
      <f7-row>
        <newboard :orientation= "color" :gameStarted="gameStarted"/>
      </f7-row>
    </div>
    <div>
      <form>
      <div><dropdown :options="usernames" :selected="object" v-on:updateOption="selectMethod" :placeholder="'Trained Model'"></dropdown></div>
      <f7-list>
      <f7-list-item checkbox value="white" checked title="Play As White" @change="isChecked"></f7-list-item>
      <f7-button @click="startGame"> Begin Game </f7-button>
      </f7-list>
      </form>
    </div>
    <!-- Tabbar for switching views-tabs -->
    <f7-toolbar tabbar labels bottom>
      <f7-link link="#" tab-link-active icon-md="material:games" text="Play"></f7-link>
      <f7-link @click="toTrain"  icon-md="material:code" text="Train"></f7-link>
      <f7-link @click="toWatch" icon-md="material:tv" text="Watch"></f7-link>
    </f7-toolbar>
  </f7-page>
</template>


<script>
import routes from '../js/routes.js';
import * as firebase from 'firebase';
import {chessboard} from 'vue-chessboard'
import 'vue-chessboard/dist/vue-chessboard.css'
import compete from "./compete.vue"
import { db } from '../js/app';
import { firebaseApp } from '../js/app';
import dropdown from 'vue-dropdowns'
import axios from 'axios'
import {userPlay} from './compete.vue'
import 'firebase/auth';

export default {
  name: "chessapp",
  data() {
      
      return {
        user: true,
        gameStarted: false,
        email: firebase.auth().currentUser.email,
        usernames: [],
        fen: '',
        color: "white",
        object: {
          name: 'Trained Model',
        } 
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
            'newboard': compete
  },
  methods: {
      onLogoutClicked() {
        firebase.auth().signOut().catch((error) =>{
          console.error("Error when trying to logout user", error);
        });  
        this.$f7.views.main.router.navigate('/');
      },
      toTrain(){
        this.$f7.views.main.router.navigate('/home/');
        this.$root.ComputerColor = "black";
        this.$root.bot = "";
        this.$root.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
        this.gameStarted = false;
      },
      toWatch(){
        this.$f7.views.main.router.navigate('/watch/');
        this.$root.ComputerColor = "black";
        this.$root.bot = "";
        this.$root.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
        this.gameStarted = false;
      },
      showInfo(data) {
      this.positionInfo = data
      },
      loadFen(fen) {
        this.currentFen = fen
      },
      startGame(){
        if(this.$root.bot==''){
          this.$f7.dialog.alert('Please select a bot before playing.');
        } else {
          this.gameStarted = true;
        }
      },
      isChecked(event){
        const self = this;
        if (event.target.checked){
          self.color="white";
          this.$root.ComputerColor="black";
          this.$root.humanColor="white";
        } else {
          self.color="black";
          this.$root.ComputerColor="white";
          this.$root.humanColor="black";
        }
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
  }

}
</script>