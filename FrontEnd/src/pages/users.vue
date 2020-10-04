<template>
  <f7-page name="users">
    <f7-navbar back-link="Back"></f7-navbar>
    <f7-block-title>Add More Users</f7-block-title>
    <f7-block strong>
      <p>Below is listed the current models that are either in the training queue or ready to be used. To begin training another player just input their Lichess Username</p>
    </f7-block>
    <div>
    <form @submit.prevent="addUsername(tmpuser)" action="" method="GET">
      <f7-list no-hairlines-md>
        <f7-list-input large class="username-input" :value="tmpuser" @input="tmpuser = $event.target.value" placeholder="Lichess Username" />
      </f7-list>
      <f7-button type ="submit"> Add New Username </f7-button>
    </form>
    </div>
    <f7-block>
       <f7-block-title style="text-align: center; font-size:large" > {{this.usernames.length}} Trained Models: </f7-block-title>
       <f7-list no-hairlines-md>
         <f7-list-item v-for="user in usernames" :key="user.id"> <p class = "text-align-center" style="font-size:large"> {{ user.username }} </p> </f7-list-item>
       </f7-list>
    </f7-block>
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
      addUsername(tmpusername) {
        db.collection('usernames').add({ 
          username: tmpusername,
          email:this.email,  
          })
      }
  }
}
</script>