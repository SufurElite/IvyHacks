
import Login from '../pages/login.vue';
import HomePage from '../pages/dash.vue';
import PlayPage from '../pages/play.vue';
import WatchPage from '../pages/watch.vue';
import NotFoundPage from '../pages/404.vue';

var routes = [
  {
    path: '/',
    component: Login,
  },
  {
    path: '/home/',
    component: HomePage,
    meta: {
      requireAuth: true
    }
  },
  {
    path: '/play/',
    component: PlayPage,
    meta: {
      requireAuth: true
    }
  },
  {
    path: '/watch/',
    component: WatchPage,
    meta: {
      requireAuth: true
    }
  },
  {
    path: '(.*)',
    component: NotFoundPage,
  },
];

export default routes;
