<template>
  <f7-page name="about">
    <f7-navbar :sliding="false" large>
      <f7-button v-on:click="onLogoutClicked" style="text-align:left; width:100%"> Logout </f7-button>
      <h4 style="text-align:right; width: 100%;">{{this.email}}</h4>
      <f7-nav-title-large sliding style="text-align:center; width: 100%;">Copy Chess</f7-nav-title-large>
    </f7-navbar>
    <f7-block-title>About My App</f7-block-title>
    <f7-block strong>
      <f7-block-header> [Insert about and training later] </f7-block-header>
    </f7-block>
    <f7-list>
      <f7-list-item title="Check/Add Models" link="/users/"></f7-list-item>
    </f7-list>
    
    <f7-block>
      <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Magni molestiae laudantium dignissimos est nobis delectus nemo ea alias voluptatum architecto, amet similique, saepe iste consectetur in repellat ut minus quibusdam!</p>
      <p>Molestias et distinctio porro nesciunt ratione similique, magni doloribus, rerum nobis, aliquam quae reiciendis quasi modi. Nam a recusandae, fugiat in ea voluptates fuga eius, velit corrupti reprehenderit dignissimos consequatur!</p>
      <p>Blanditiis, cumque quo adipisci. Molestiae, dolores dolorum quos doloremque ipsa ullam eligendi commodi deserunt doloribus inventore magni? Ea mollitia veniam nostrum nihil, iusto doloribus a at! Ea molestiae ullam delectus!</p>
    </f7-block>
    <!-- Tabbar for switching views-tabs -->
    
    <f7-toolbar tabbar labels bottom>
      <f7-link @click="toPlay" icon-md="material:games" text="Play"></f7-link>
      <f7-link link="#" tab-link-active icon-md="material:code" text="Train"></f7-link>
      <f7-link @click="toWatch" icon-md="material:tv" text="Watch"></f7-link>
    </f7-toolbar>
  </f7-page>
</template>
<script>
import routes from '../js/routes.js';
import firebase from 'firebase';
import { db } from '../js/app'
import 'firebase/auth';
import dropdown from 'vue-dropdowns'

export default {
  
  data() {
      return {
        user: true,
        email: firebase.auth().currentUser.email,
        usernames: [],
        tmpuser: '',
        object: {
          name: 'Lichess Username',
        }
      };
    },
    firestore () {
      return {
        usernames: db.collection("usernames").where("email", "==", this.email)
      }
    },
     components: {
            'dropdown': dropdown,
      },
      methods: {
      onLogoutClicked() {
        firebase.auth().signOut().catch((error) =>{
          console.error("Error when trying to logout user", error);
        });  
        this.$f7.views.main.router.navigate('/');
      },
      addUsername(tmpusername) {
        db.collection('usernames').add({ 
          username: tmpusername,
          email:this.email,  
          })
      },
      selectMethod(payload){
        this.object.name = payload.username;
        this.$root.bot = payload.username;
        this.$root.bot2 = payload.username;
      },
      toPlay(){
        this.$f7.views.main.router.navigate('/play/');
      },
      toUsers(){
        this.$f7.views.main.router.navigate('/users/');
      },
      toWatch(){
        this.$f7.views.main.router.navigate('/watch/');
      }
  }
}
</script>