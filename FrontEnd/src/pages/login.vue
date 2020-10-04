<template>
  <f7-page name="home">
  <!-- Top Navbar -->
    <f7-navbar :sliding="false" large>
      <f7-nav-title-large sliding style="text-align:center; width: 100%;">Copy Chess</f7-nav-title-large>
    </f7-navbar>

  <!-- Page content-->
  <f7-block v-if="user" strong>
    <f7-block-header> You are logged in as {{user.displayName}} {{user.email}} </f7-block-header>
    <f7-button v-on:click="onLogoutClicked"> Logout </f7-button>
  </f7-block>
  <f7-block v-else strong>
    <form @submit.prevent="onLoginWithEmailClicked" action="" method="GET">
    <f7-list class = "login-list" no-hairlines-md>
      <f7-list-input class = "email-input" :value="email" @input="email = $event.target.value" label="Login with your email address" type="email" placeholder="Email Address" />
      <f7-list-input :value="password" @input="password = $event.target.value" label="Provide your password" type="password" placeholder="Password" />
    </f7-list>
    <f7-button fill type ="submit"> Login </f7-button>
    </form>
  </f7-block>

  <f7-block v-if="!user" strong>
    <f7-block-title> No account yet? </f7-block-title>
    <f7-button v-if="!showSignupForm" fill v-on:click="showSignupForm = true"> Create new account </f7-button>
    <form @submit.prevent="onSignupClicked" action="" method="GET">
      <f7-list v-if="showSignupForm" class = "login-list" no-hairlines-md>
        <f7-list-input class="email-input" :value="email_signup" @input="email_signup = $event.target.value" label="Type in your email address" type="email" placeholder="E-mail" />
        <f7-list-input :value="password_signup" @input="password_signup = $event.target.value" label="Choose a password" type ="password" placeholder="Password" />
        <!--<f7-list-input class="lichess-input" :value="lichess_signup" @input="lichess_signup = $event.target.value" label="Type in your Lichess Username" type="username" placeholder="E-mail" />-->
      </f7-list>
      <f7-button v-if="showSignupForm" fill type ="submit"> Sign up </f7-button>
    </form>
  </f7-block>
  <!---
  <f7-block v-if="!user" strong>
    <f7-block-title> Other login methods </f7-block-title>
    <f7-button color = "red" fill v-on:click="onGoogleLoginClicked"> Sign in with Google </f7-button>
  </f7-block>
  -->
  </f7-page>

</template>

<script> 
  import routes from '../js/routes.js';
  import uData from '../js/routes.js';
  import * as firebase from 'firebase';
  import { db } from '../js/app'
  //import VueFire from 'vuefire'
  //import 'firebase/firestore'
  import 'firebase/auth';

  export default{

    data() {
      
      return {
        user: null,
        email: '', 
        password: '',
        email_signup: '',
        password_signup: '',
        showSignupForm: false,
      };
    },
    methods: {
      goBack() {
        this.$f7.loginScreen.close();
      },
      onLoginWithEmailClicked() {
      firebase.auth().signInWithEmailAndPassword(this.email, this.password).then((res) => {
        this.user = firebase.auth().currentUser.user;
        //uData.email = this.user.email;
        //alert(uData.email);
        this.$root.email = this.email;
        this.$f7.views.main.router.navigate('/home/');
      }).catch((error) => {
        console.error('Failed to login user', error);
        this.$7.dialog.alert(error.message + ' Please try again.');
      });
      },
      onSignupClicked(e){
        e.preventDefault();
        firebase.auth().createUserWithEmailAndPassword(this.email_signup,this.password_signup).catch((error)=>{
          console.error("Failed to create user", error);
          this.$f7.dialog.alert(error.message + '. Please try again.', '');
        });

      },
      onLogoutClicked() {
        firebase.auth().signOut().catch((error) =>{
          console.error("Error when trying to logout user", error);
        });
      },

    },
    mounted() {
      // For Firebase JS SDK v7.20.0 and later, measurementId is optional
      // Fired when user logs in or out
      firebase.auth().onAuthStateChanged((user) => {
        console.log("User auth status has changed!", user);
        this.user = user;
        if(user!=null){
          //this.router.push()
        }
      });
    },
  };

</script>