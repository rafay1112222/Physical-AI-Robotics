import React from 'react';
import Layout from '@theme-init/Layout';
import Chatbot from '@site/src/components/Chatbot';

export default function CustomLayout(props) {
  return (
    <Layout {...props}>
      {props.children}
      <Chatbot />
    </Layout>
  );
}