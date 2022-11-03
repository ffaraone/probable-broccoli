/*
Copyright (c) 2022, Globex Corporation
All rights reserved.
*/
import createApp, {
  Card,
} from '@cloudblueconnect/connect-ui-toolkit';
import {
  settings,
} from '../pages';
import '@fontsource/roboto/500.css';
import '../../styles/index.css';


createApp({ 'settings-card': Card })
  .then(settings);
