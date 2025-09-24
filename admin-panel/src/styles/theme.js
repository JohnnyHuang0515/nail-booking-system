import { createTheme } from '@mui/material/styles';

// 美甲產業淡淡可愛俏皮主題 - 玻璃暈染感
const theme = createTheme({
  palette: {
    primary: {
      main: '#F5E6D3', // 溫柔奶茶色
      light: '#FAF0E6', // 淺奶茶色
      dark: '#E8D5C4', // 深奶茶色
      contrastText: '#8B6F47',
    },
    secondary: {
      main: '#FFB6C1', // 淺粉紅
      light: '#FFC0CB', // 更淺的粉紅
      dark: '#FF91A4', // 深粉紅
      contrastText: '#8B6F47',
    },
    accent: {
      main: '#B0E0E6', // 淺藍
      light: '#C7E8ED', // 更淺的藍
      dark: '#87CEEB', // 深藍
    },
    glass: {
      main: 'rgba(255, 255, 255, 0.3)', // 玻璃白
      light: 'rgba(255, 255, 255, 0.2)', // 更淡的玻璃
      dark: 'rgba(255, 255, 255, 0.4)', // 稍深的玻璃
    },
    background: {
      default: '#FFFEF7', // 溫暖的米白色
      paper: 'rgba(255, 255, 255, 0.8)', // 半透明白色
    },
    text: {
      primary: '#8B6F47', // 溫暖的棕色
      secondary: '#A68B5B', // 淺棕色
    },
  },
  typography: {
    fontFamily: 'Roboto, "Noto Sans TC", Arial, sans-serif',
    h1: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
    h2: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
    h3: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
    h4: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
    h5: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
    h6: { fontFamily: '"Noto Sans TC", Roboto, Arial, sans-serif' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: `
            radial-gradient(circle at 20% 20%, rgba(255, 182, 193, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(176, 224, 230, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(245, 230, 211, 0.15) 0%, transparent 50%),
            linear-gradient(135deg, #FFFEF7 0%, #FAF0E6 100%)
          `,
          minHeight: '100vh',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 32px rgba(255, 182, 193, 0.15)',
          border: '1px solid rgba(255, 182, 193, 0.2)',
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(10px)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '1px',
            background: 'linear-gradient(90deg, transparent, rgba(255, 182, 193, 0.3), transparent)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 24px',
          fontSize: '14px',
          boxShadow: '0 4px 15px rgba(255, 182, 193, 0.2)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 25px rgba(255, 182, 193, 0.3)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #F5E6D3 0%, #FFB6C1 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #E8D5C4 0%, #FF91A4 100%)',
          },
        },
        outlined: {
          border: '1px solid rgba(255, 182, 193, 0.5)',
          color: '#8B6F47',
          background: 'rgba(255, 255, 255, 0.3)',
          backdropFilter: 'blur(5px)',
          '&:hover': {
            border: '1px solid #FFB6C1',
            background: 'rgba(255, 182, 193, 0.1)',
          },
        },
      },
    },
  },
});

export default theme;
