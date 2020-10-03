<template>
  <f7-page name="about">
    <f7-navbar :sliding="false" large>
      <f7-button v-on:click="onLogoutClicked" style="text-align:left"> Logout </f7-button>
      <f7-nav-title-large sliding style="text-align:center; width: 100%;">Copy Chess</f7-nav-title-large>
    </f7-navbar>
    
    <div id="chessapp" style="display: flex;align-items: center;justify-content: center;">
      <f7-row>
        <chessboard></chessboard>
      </f7-row>
    </div>
    <div>
        Should be here:
      <dropdown :options="usernames" :selected="object" v-on:updateOption="selectMethod" :placeholder="'Lichess Username'"></dropdown>
      <h1>You are logged in as {{this.usernames.length}} </h1>
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
import newboard from "./newboard.vue"
import { db } from '../js/app';
import { firebaseApp } from '../js/app';
import dropdown from 'vue-dropdowns'
import 'firebase/auth';
export default {
  name: "chessapp",
  components: {
    chessboard,
    newboard,
  },
  data() {
      
      return {
        user: true,
        email: firebase.auth().currentUser.email,
        usernames: [],
        object: {
          name: 'Lichess Username',
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
            'chessboard': chessboard
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
      },
      toWatch(){
        this.$f7.views.main.router.navigate('/watch/');
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
      },
  },
  created() {
    this.fens = ['5rr1/3nqpk1/p3p2p/Pp1pP1pP/2pP1PN1/2P1Q3/2P3P1/R4RK1 b - f3 0 28',
                'r4rk1/pp1b3p/6p1/8/3NpP2/1P4P1/P2K3P/R6R w - - 0 22'
                ]
  }

}
</script>