import React, { Component, Suspense } from 'react';
import { Route, Navigate, Routes } from 'react-router-dom';


import { Welcome } from './pages/Welcome';
import { Login } from './pages/Login';

import { DocList } from './pages/Doc_List';
import { DocEdit } from './pages/Doc_Edit';
import { DocView } from './pages/Doc_View';


export class Router extends Component {
    componentDidMount() {
      
    }
  
    componentDidUpdate() {
      
    }
  
    render() {
      
      return (
        <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/login" element={<Login />} />

            <Route path="/doc" element={<DocList />} />
            <Route path="/doc/create" element={<DocEdit mode="create" />} />
            <Route path="/doc/:docId" element={<DocView />} />

        </Routes>
      )
    }
}