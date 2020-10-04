<script>
import { chessboard }  from 'vue-chessboard'
import axios from 'axios'
export default {
  name: 'watchbot',
  extends: chessboard,
  props:{
    gameStarted: false
  },
  methods: {
    aiPlay() {
          this.compMove(this.$root.bot, "white")
    },
    compMove(bot) {
      axios.post('http://127.0.0.1:5000/predict', {
        name: bot,
        fen: this.game.fen()
      }).then((response)=>{
        console.log(response.data);
        let moves = this.game.moves({verbose: true})
        var tmp = {from: response.data["from"], to: response.data["to"], promotion: this.promoteTo}
        this.game.move(tmp)
        var otherBot = ""
        var color = ""
        if(this.$root.bot == bot){
          otherBot = this.$root.bot2;
          color = "black"
        } else {
          otherBot = this.$root.bot;
          color = "white"
        }
        this.board.set({
        fen: response.data["fen"],
        turnColor: color,
        movable: {
          color: color,
          dests: this.possibleMoves(),
          events: { after: this.compMove(otherBot)},
        }
      });
      })
    },
    aiNextMove() {
      this.$root.fen=this.game.fen();
      //console.log(this.toColor())
      var move = this.compMove()
     
    }
  },
  mounted() {
    this.board.set({
      movable: { events: { after: this.aiPlay()} },
    })
  },
  watch: {
    gameStarted: function(){
        this.board.set({
        movable: { events: { after: this.aiPlay()} },
      })
    }
  }
}
</script>