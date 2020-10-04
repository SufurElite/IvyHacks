<script>
import { chessboard }  from 'vue-chessboard'
import axios from 'axios'
export default {
  name: 'compete',
  extends: chessboard,
  props:{
    gameStarted: false
  },
  methods: {
    userPlay() {
        return (orig, dest) => {
          if (this.isPromotion(orig, dest)) {
            this.promoteTo = this.onPromotion()
          }
          //console.log({from: orig, to: dest, promotion: this.promoteTo})
          this.game.move({from: orig, to: dest, promotion: this.promoteTo}) // promote to queen for simplicity
          this.board.set({
            fen: this.game.fen()
          })
          this.$root.fen = this.game.fen()
          this.calculatePromotions()
          this.compMove()
        };
    },
    compMove() {
      axios.post('http://127.0.0.1:5000/predict', {
        name: this.$root.bot,
        fen: this.game.fen()
      }).then((response)=>{
        console.log(response.data);
        let moves = this.game.moves({verbose: true})
        var tmp = {from: response.data["from"], to: response.data["to"], promotion: this.promoteTo}
        this.game.move(tmp)
    
        this.board.set({
        fen: response.data["fen"],
        turnColor: this.$root.humanColor,
        movable: {
          color: this.$root.humanColor,
          dests: this.possibleMoves(),
          events: { after: this.userPlay()},
        }
      });
        
        return response.data;  
      })
    },
    aiNextMove() {
      this.$root.fen=this.game.fen();
      //console.log(this.toColor())
      var move = this.compMove()
     
    }
  },
  watch: {
    gameStarted: function(){
      if(this.$root.ComputerColor=="black"){
        this.board.set({
        movable: { events: { after: this.userPlay()} },
      })
      } else{
        console.log(this.$root.humanColor)
        this.board.set({
        movable: { events: { after: this.compMove()} },
      })
      }
    }
  }
  /*
  if(gameStarted){
      alert(gameStarted)
    
    }
  */
}
</script>