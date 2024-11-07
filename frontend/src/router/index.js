import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

router.beforeEach((to, from, next) => {
  const code = to.query.code;
  if (code) {
    const { code, ...queryWithoutCode } = to.query;
    router.replace({ path: to.path });

    axios.post('http://localhost:5000/callback', { code })
      .then(response => {
        const access_token = response.data.token.access_token;
        const refresh_token = response.data.token.refresh_token;

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('isUserLoggedIn', true);

        const user = response.data.user_info;
        const username = user.preferred_username;

        console.log('bocs username', username)
        next();
      })
      .catch(error => {
        console.error("Error during login callback:", error);
        next();
      });
  } else {
    next();
  }
});


export default router
